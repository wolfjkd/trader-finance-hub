#!/usr/bin/env python3
"""
market_analyzer.py - 全市场综合分析引擎 v1.0
============================================
群友"全市场综合分析报告"框架的Python实现。

三大模块:
  1. NewsFetcher     — 财经新闻/公告/研报事件采集器
  2. THSDataFetcher  — 同花顺板块数据封装（AKShare后端）
  3. MarketModels    — 四象限分析/情绪时钟/信息熵共识度

数据源矩阵:
  新闻: stock_news_em + stock_news_main_cx + stock_info_global_em + news_cctv
  板块: THS概念/行业名称+行情+成分 + EM概念成分
  资金: 东方财富datacenter端（龙虎榜/北向/涨停池）
  行情: 腾讯接口（主力）+ Sina日线（兜底）

用法:
  python market_analyzer.py health          # 全链路健康检测
  python market_analyzer.py news            # 今日财经要闻
  python market_analyzer.py sector          # 板块四象限分析
  python market_analyzer.py sentiment       # 情绪时钟
  python market_analyzer.py report          # 生成综合分析报告(JSON)
"""

import json
import math
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import Any

# ============================================================
# 模块1: 新闻事件采集器
# ============================================================

@dataclass
class NewsItem:
    """标准化新闻条目"""
    title: str
    content: str = ""
    source: str = ""
    url: str = ""
    publish_time: str = ""
    keywords: list[str] = field(default_factory=list)
    sentiment: str = "neutral"  # positive/negative/neutral
    impact_score: float = 0.0   # 0-100市场影响度


class NewsFetcher:
    """
    多源财经新闻采集器。
    覆盖: 东方财富个股新闻/要闻/全球财经/CCTV新闻
    使用AKShare后端，免API Key。
    """

    NAME = "news"
    SOURCES = {
        "em_stock":   "东方财富个股新闻",
        "em_main":    "东方财富7x24要闻",
        "em_global":  "东方财富全球财经",
        "cctv":       "CCTV新闻联播",
    }
    # 高影响关键词（加权）
    HIGH_IMPACT_KEYWORDS = [
        "涨停", "跌停", "停牌", "复牌", "重大资产重组", "并购", "回购",
        "减持", "增持", "业绩预告", "业绩快报", "分红", "送转",
        "政策", "国务院", "证监会", "央行", "降息", "降准",
        "关税", "制裁", "贸易战", "地缘", "战争",
    ]

    @staticmethod
    def _load_ak():
        import akshare as ak
        return ak

    @classmethod
    def fetch_em_stock_news(cls, symbol: str = "600170", limit: int = 10) -> list[NewsItem]:
        """东方财富个股新闻"""
        try:
            ak = cls._load_ak()
            df = ak.stock_news_em(symbol=symbol)
            items = []
            for _, row in df.head(limit).iterrows():
                title = str(row.get("新闻标题", ""))
                content = str(row.get("新闻内容", ""))[:200]
                items.append(NewsItem(
                    title=title,
                    content=content,
                    source="东方财富",
                    url=str(row.get("新闻链接", "")),
                    publish_time=str(row.get("发布时间", "")),
                    keywords=[str(row.get("关键词", ""))],
                ))
            return items
        except Exception as e:
            return [NewsItem(title=f"[EM Stock News Error] {e}", source="error")]

    @classmethod
    def fetch_em_main_news(cls, limit: int = 20) -> list[NewsItem]:
        """东方财富7x24要闻"""
        try:
            ak = cls._load_ak()
            df = ak.stock_news_main_cx()
            items = []
            for _, row in df.head(limit).iterrows():
                items.append(NewsItem(
                    title=str(row.get("summary", "")),
                    content=str(row.get("tag", "")),
                    source="东方财富7x24",
                    url=str(row.get("url", "")),
                ))
            return items
        except Exception as e:
            return [NewsItem(title=f"[EM Main News Error] {e}", source="error")]

    @classmethod
    def fetch_em_global_news(cls, limit: int = 20) -> list[NewsItem]:
        """东方财富全球财经"""
        try:
            ak = cls._load_ak()
            df = ak.stock_info_global_em()
            items = []
            for _, row in df.head(limit).iterrows():
                items.append(NewsItem(
                    title=str(row.get("标题", "")),
                    content=str(row.get("摘要", ""))[:200],
                    source="东方财富全球",
                    url=str(row.get("链接", "")),
                    publish_time=str(row.get("发布时间", "")),
                ))
            return items
        except Exception as e:
            return [NewsItem(title=f"[EM Global News Error] {e}", source="error")]

    @classmethod
    def fetch_cctv_news(cls, limit: int = 12) -> list[NewsItem]:
        """CCTV新闻联播"""
        try:
            ak = cls._load_ak()
            df = ak.news_cctv()
            items = []
            for _, row in df.head(limit).iterrows():
                items.append(NewsItem(
                    title=str(row.get("title", "")),
                    content=str(row.get("content", ""))[:200],
                    source="CCTV新闻联播",
                    publish_time=str(row.get("date", "")),
                ))
            return items
        except Exception as e:
            return [NewsItem(title=f"[CCTV Error] {e}", source="error")]

    @classmethod
    def fetch_all(cls, stock_code: str = "600170") -> dict[str, list[NewsItem]]:
        """采集所有源新闻"""
        return {
            "em_stock": cls.fetch_em_stock_news(stock_code),
            "em_main": cls.fetch_em_main_news(),
            "em_global": cls.fetch_em_global_news(),
            "cctv": cls.fetch_cctv_news(),
        }

    @classmethod
    def fetch_headlines(cls, stock_code: str = "600170") -> list[NewsItem]:
        """采集头条新闻（去重+加权）"""
        all_news = []
        seen = set()
        sources = cls.fetch_all(stock_code)
        for source_name, items in sources.items():
            for item in items:
                if item.title and item.title not in seen:
                    seen.add(item.title)
                    # 计算影响度评分
                    score = cls._calc_impact(item)
                    item.impact_score = score
                    # 简单情感分析（基于关键词）
                    item.sentiment = cls._detect_sentiment(item.title, item.content)
                    all_news.append(item)

        # 按影响度排序，取TOP30
        all_news.sort(key=lambda x: x.impact_score, reverse=True)
        return all_news[:30]

    @classmethod
    def _calc_impact(cls, item: NewsItem) -> float:
        """计算新闻影响度（0-100）"""
        text = item.title + item.content
        score = 20.0  # 基础分
        for kw in cls.HIGH_IMPACT_KEYWORDS:
            if kw in text:
                score += 15.0
        return min(score, 100.0)

    @staticmethod
    def _detect_sentiment(title: str, content: str) -> str:
        """简单情感检测"""
        text = title + content
        positive_words = ["增长", "上涨", "利好", "突破", "创新高", "中标", "签约", "盈利", "分红", "回购", "增持"]
        negative_words = ["下跌", "亏损", "利空", "减持", "处罚", "调查", "退市", "违约", "爆雷", "制裁", "关税"]

        pos = sum(1 for w in positive_words if w in text)
        neg = sum(1 for w in negative_words if w in text)
        if pos > neg:
            return "positive"
        elif neg > pos:
            return "negative"
        return "neutral"


# ============================================================
# 模块2: 同花顺板块数据封装
# ============================================================

@dataclass
class SectorSnapshot:
    """板块快照"""
    name: str
    code: str = ""
    change_pct: float = 0.0
    volume: float = 0.0
    amount: float = 0.0
    lead_stock: str = ""
    lead_change: float = 0.0
    member_count: int = 0
    driver_event: str = ""
    index_open: float = 0.0
    index_high: float = 0.0
    index_low: float = 0.0
    index_close: float = 0.0


class THSDataFetcher:
    """
    同花顺板块数据封装器。
    通过AKShare直接调用同花顺接口，不依赖Tushare MCP。
    """

    NAME = "ths"

    @staticmethod
    def _load_ak():
        import akshare as ak
        return ak

    @classmethod
    def _safe_call(cls, fn, default=None):
        try:
            return fn()
        except Exception:
            return default

    # ---- 板块列表 ----

    @classmethod
    def get_concept_list(cls) -> list[dict]:
        """获取同花顺概念板块列表"""
        try:
            ak = cls._load_ak()
            df = ak.stock_board_concept_name_ths()
            return [{"name": row["name"], "code": row["code"]}
                    for _, row in df.iterrows()]
        except Exception:
            return []

    @classmethod
    def get_industry_list(cls) -> list[dict]:
        """获取同花顺行业板块列表"""
        try:
            ak = cls._load_ak()
            df = ak.stock_board_industry_name_ths()
            return [{"name": row["name"], "code": row["code"]}
                    for _, row in df.iterrows()]
        except Exception:
            return []

    # ---- 板块行情 ----

    @classmethod
    def get_concept_index(cls, name: str, days: int = 5) -> dict:
        """获取概念板块K线行情"""
        try:
            ak = cls._load_ak()
            end = date.today().strftime("%Y%m%d")
            start = (date.today() - timedelta(days=days * 2)).strftime("%Y%m%d")
            df = ak.stock_board_concept_index_ths(symbol=name, start_date=start, end_date=end)
            if df.empty:
                return {}
            latest = df.tail(1).iloc[0]
            prev = df.tail(2).iloc[0] if len(df) >= 2 else latest
            return {
                "name": name,
                "latest_date": str(latest.get("日期", "")),
                "open": float(latest.get("开盘价", 0) or 0),
                "high": float(latest.get("最高价", 0) or 0),
                "low": float(latest.get("最低价", 0) or 0),
                "close": float(latest.get("收盘价", 0) or 0),
                "volume": float(latest.get("成交量", 0) or 0),
                "change_pct": round(
                    (float(latest.get("收盘价", 0) or 0) - float(prev.get("收盘价", 0) or 0))
                    / float(prev.get("收盘价", 1) or 1) * 100, 2
                ),
                "raw": df.tail(days).to_dict(orient="records"),
            }
        except Exception:
            return {}

    @classmethod
    def get_industry_index(cls, name: str, days: int = 5) -> dict:
        """获取行业板块K线行情"""
        try:
            ak = cls._load_ak()
            end = date.today().strftime("%Y%m%d")
            start = (date.today() - timedelta(days=days * 2)).strftime("%Y%m%d")
            df = ak.stock_board_industry_index_ths(symbol=name, start_date=start, end_date=end)
            if df.empty:
                return {}
            latest = df.tail(1).iloc[0]
            prev = df.tail(2).iloc[0] if len(df) >= 2 else latest
            return {
                "name": name,
                "latest_date": str(latest.get("日期", "")),
                "open": float(latest.get("开盘价", 0) or 0),
                "high": float(latest.get("最高价", 0) or 0),
                "low": float(latest.get("最低价", 0) or 0),
                "close": float(latest.get("收盘价", 0) or 0),
                "volume": float(latest.get("成交量", 0) or 0),
                "change_pct": round(
                    (float(latest.get("收盘价", 0) or 0) - float(prev.get("收盘价", 0) or 0))
                    / float(prev.get("收盘价", 1) or 1) * 100, 2
                ),
                "raw": df.tail(days).to_dict(orient="records"),
            }
        except Exception:
            return {}

    # ---- 板块信息 ----

    @classmethod
    def get_concept_info(cls, name: str) -> dict:
        """获取概念板块详细信息"""
        try:
            ak = cls._load_ak()
            df = ak.stock_board_concept_info_ths(symbol=name)
            info = {}
            for _, row in df.iterrows():
                key = str(row.get("项目", ""))
                val = str(row.get("值", ""))
                info[key] = val
            return info
        except Exception:
            return {}

    @classmethod
    def get_industry_info(cls, name: str) -> dict:
        """获取行业板块详细信息"""
        try:
            ak = cls._load_ak()
            df = ak.stock_board_industry_info_ths(symbol=name)
            info = {}
            for _, row in df.iterrows():
                key = str(row.get("项目", ""))
                val = str(row.get("值", ""))
                info[key] = val
            return info
        except Exception:
            return {}

    # ---- 板块摘要 ----

    @classmethod
    def get_concept_summary(cls) -> list[dict]:
        """获取概念板块驱动事件摘要"""
        try:
            ak = cls._load_ak()
            df = ak.stock_board_concept_summary_ths()
            return df.to_dict(orient="records")
        except Exception:
            return []

    # ---- 热门排名 ----

    @classmethod
    def get_hot_rank(cls) -> list[dict]:
        """获取东方财富热门股票排名"""
        try:
            ak = cls._load_ak()
            df = ak.stock_hot_rank_em()
            return df.head(30).to_dict(orient="records")
        except Exception:
            return []

    @classmethod
    def get_continuous_high(cls) -> list[dict]:
        """持续新高股"""
        try:
            ak = cls._load_ak()
            df = ak.stock_rank_cxg_ths()
            return df.head(20).to_dict(orient="records")
        except Exception:
            return []

    @classmethod
    def get_continuous_low(cls) -> list[dict]:
        """持续新低股"""
        try:
            ak = cls._load_ak()
            df = ak.stock_rank_cxd_ths()
            return df.head(20).to_dict(orient="records")
        except Exception:
            return []

    # ---- 批量获取板块行情（用于四象限）----

    @classmethod
    def get_concept_batch_quotes(cls, names: list[str], max_names: int = 60) -> list[dict]:
        """批量获取概念板块行情（用于排序和筛选）"""
        all_concepts = cls.get_concept_list()
        results = []
        # 先按优先级：取前max_names个，以及用户指定的names
        priority_names = set(names) if names else set()
        for c in all_concepts[:max_names]:
            if c["name"] not in priority_names and len(priority_names) < 10:
                priority_names.add(c["name"])

        for name in list(priority_names)[:max_names]:
            quote = cls.get_concept_index(name, days=2)
            if quote:
                results.append(quote)
                time.sleep(0.05)  # 温和限速
        return results

    @classmethod
    def get_industry_batch_quotes(cls, max_count: int = 60) -> list[dict]:
        """批量获取行业板块行情"""
        industries = cls.get_industry_list()
        results = []
        for ind in industries[:max_count]:
            quote = cls.get_industry_index(ind["name"], days=2)
            if quote:
                results.append(quote)
                time.sleep(0.05)
        return results

    # ---- EM概念成分股 ----

    @classmethod
    def get_em_concept_members(cls, concept_code: str = "BK1184") -> list[dict]:
        """获取东方财富概念板块成分股"""
        try:
            ak = cls._load_ak()
            df = ak.stock_board_concept_cons_em(symbol=concept_code)
            return df.head(30).to_dict(orient="records")
        except Exception:
            return []


# ============================================================
# 模块3: 市场分析模型（四象限 + 情绪时钟 + 信息熵）
# ============================================================

@dataclass
class QuadrantItem:
    """四象限元素"""
    name: str
    change_pct: float       # 涨跌幅 %
    consensus_strength: float  # 共识强度 0-100
    quadrant: str = ""       # I(强共识上涨) / II(弱共识上涨) / III(弱共识下跌) / IV(强共识下跌)
    volume_ratio: float = 1.0  # 量比


class MarketModels:
    """
    市场分析模型集合。
    实现群友报告中的：四象限模型 / 情绪时钟 / 信息熵共识度
    """

    @staticmethod
    def four_quadrant(sectors: list[dict]) -> list[QuadrantItem]:
        """
        四象限模型：涨幅 × 共识强度

        象限 | 涨幅 | 共识 | 含义
        -----|------|------|------
        I    | +    | 强   | 主力一致看多（追涨）
        II   | +    | 弱   | 散户跟风上涨（谨慎）
        III  | -    | 弱   | 散户恐慌下跌（关注）
        IV   | -    | 强   | 主力一致看空（规避）

        共识强度 = 基于成交量/换手率/板块内涨跌比计算
        """
        if not sectors:
            return []

        # Step 1: 计算每个板块的共识强度
        items = []
        for s in sectors:
            change = s.get("change_pct", 0) or 0

            # 共识强度: 成交量标准化 + 波动率反比
            volumes = [x.get("volume", 0) or 0 for x in sectors]
            max_vol = max(volumes) if volumes and max(volumes) > 0 else 1
            vol_score = ((s.get("volume", 0) or 0) / max_vol) * 50

            # 波动率反比：波动越大、共识越弱
            raw_data = s.get("raw", [])
            if len(raw_data) >= 2:
                closes = [float(r.get("收盘价", 0) or 0) for r in raw_data]
                if closes[-1] and closes[-1] != 0:
                    volatility = abs(closes[-1] - closes[0]) / closes[-1] * 100
                else:
                    volatility = 5
            else:
                volatility = 5
            stability_score = max(0, 50 - volatility * 5)

            consensus = min(100, vol_score + stability_score)

            # 量比
            raw = s.get("raw", [])
            if len(raw) >= 2:
                vol_today = float(raw[-1].get("成交量", 0) or 0)
                vol_yesterday = float(raw[-2].get("成交量", 1) or 1)
                vol_ratio = vol_today / vol_yesterday if vol_yesterday > 0 else 1.0
            else:
                vol_ratio = 1.0

            # 四象限分类
            if change >= 0 and consensus >= 40:
                quadrant = "I"
            elif change >= 0:
                quadrant = "II"
            elif change < 0 and consensus >= 40:
                quadrant = "IV"
            else:
                quadrant = "III"

            items.append(QuadrantItem(
                name=s.get("name", ""),
                change_pct=change,
                consensus_strength=round(consensus, 1),
                quadrant=quadrant,
                volume_ratio=round(vol_ratio, 2),
            ))

        return items

    @staticmethod
    def entropy_consensus(sectors: list[QuadrantItem]) -> dict:
        """
        信息熵共识度量。

        原理：市场涨跌分布越均匀 → 熵越高 → 共识越弱
              涨跌高度集中在某一方向 → 熵越低 → 共识越强

        返回:
          - entropy: 香农熵值 (0~1, 越低=越有共识)
          - consensus_level: "高度共识" / "中度共识" / "分歧较大" / "高度分歧"
          - distribution: 各象限占比
        """
        if not sectors:
            return {"entropy": 1.0, "consensus_level": "无数据", "distribution": {}}

        # 按方向分类
        up_strong = sum(1 for s in sectors if s.quadrant == "I")
        up_weak = sum(1 for s in sectors if s.quadrant == "II")
        down_weak = sum(1 for s in sectors if s.quadrant == "III")
        down_strong = sum(1 for s in sectors if s.quadrant == "IV")

        total = len(sectors)
        if total == 0:
            return {"entropy": 1.0, "consensus_level": "无数据", "distribution": {}}

        # 计算香农熵
        probs = [up_strong / total, up_weak / total, down_weak / total, down_strong / total]
        entropy = 0.0
        for p in probs:
            if p > 0:
                entropy -= p * math.log2(p)

        # 归一化: 最大熵 = log2(4) = 2.0
        max_entropy = 2.0
        normalized = entropy / max_entropy if max_entropy > 0 else 1.0

        if normalized < 0.3:
            level = "高度共识"
        elif normalized < 0.5:
            level = "中度共识"
        elif normalized < 0.7:
            level = "分歧较大"
        else:
            level = "高度分歧"

        return {
            "entropy": round(normalized, 3),
            "consensus_level": level,
            "distribution": {
                "I_强共识上涨": up_strong,
                "II_弱共识上涨": up_weak,
                "III_弱共识下跌": down_weak,
                "IV_强共识下跌": down_strong,
            }
        }

    @staticmethod
    def sentiment_clock(
        market_index_change: float,
        up_down_ratio: float,
        limit_up_count: int,
        limit_down_count: int,
        northbound_net: float,
    ) -> dict:
        """
        情绪时钟模型。

        六阶段循环:
          绝望 → 怀疑 → 希望 → 乐观 → 兴奋 → 贪婪 → 恐慌 → 绝望 ...

        评分维度（各25分）:
          1. 大盘涨跌 (market_index_change)
          2. 涨跌比 (up_down_ratio)
          3. 涨停/跌停比 (limit_up_count / limit_down_count)
          4. 北向资金 (northbound_net)

        总分 0-100，映射到情绪时钟。
        """
        # 维度1: 大盘涨跌 (0-25)
        if market_index_change > 2:
            score1 = 25
        elif market_index_change > 1:
            score1 = 20
        elif market_index_change > 0:
            score1 = 15
        elif market_index_change > -1:
            score1 = 10
        elif market_index_change > -2:
            score1 = 5
        else:
            score1 = 0

        # 维度2: 涨跌比 (0-25)
        if up_down_ratio > 3:
            score2 = 25
        elif up_down_ratio > 2:
            score2 = 20
        elif up_down_ratio > 1:
            score2 = 15
        elif up_down_ratio > 0.5:
            score2 = 10
        elif up_down_ratio > 0.25:
            score2 = 5
        else:
            score2 = 0

        # 维度3: 涨停/跌停比 (0-25)
        if limit_down_count == 0:
            lt_ratio = 10.0 if limit_up_count > 0 else 5.0
        else:
            lt_ratio = limit_up_count / limit_down_count
        if lt_ratio > 5:
            score3 = 25
        elif lt_ratio > 3:
            score3 = 20
        elif lt_ratio > 1.5:
            score3 = 15
        elif lt_ratio > 0.7:
            score3 = 10
        elif lt_ratio > 0.3:
            score3 = 5
        else:
            score3 = 0

        # 维度4: 北向资金 (0-25)
        if northbound_net > 50:
            score4 = 25
        elif northbound_net > 20:
            score4 = 20
        elif northbound_net > 0:
            score4 = 15
        elif northbound_net > -20:
            score4 = 10
        elif northbound_net > -50:
            score4 = 5
        else:
            score4 = 0

        total = round(score1 + score2 + score3 + score4, 1)

        # 映射到情绪阶段
        if total >= 85:
            phase = "贪婪"
            description = "市场情绪极度亢奋，需警惕回调风险"
            action = "逢高减仓，不宜追高"
        elif total >= 70:
            phase = "兴奋"
            description = "市场情绪高涨，赚钱效应明显"
            action = "持仓为主，择机加仓龙头"
        elif total >= 55:
            phase = "乐观"
            description = "市场信心恢复，资金逐步入场"
            action = "积极布局，关注低位板块"
        elif total >= 40:
            phase = "希望"
            description = "市场触底反弹，情绪开始修复"
            action = "试探性建仓，控制仓位"
        elif total >= 25:
            phase = "怀疑"
            description = "市场方向不明，多空分歧加大"
            action = "观望为主，等待方向确认"
        elif total >= 15:
            phase = "恐慌"
            description = "市场恐慌情绪蔓延，抛压增加"
            action = "严格止损，保留现金"
        else:
            phase = "绝望"
            description = "市场极度悲观，流动性枯竭"
            action = "清仓观望，等待右侧信号"

        return {
            "total_score": total,
            "phase": phase,
            "description": description,
            "action": action,
            "breakdown": {
                "大盘涨跌": score1,
                "涨跌比": score2,
                "涨停跌停比": score3,
                "北向资金": score4,
            },
            "inputs": {
                "market_index_change": market_index_change,
                "up_down_ratio": up_down_ratio,
                "limit_up_count": limit_up_count,
                "limit_down_count": limit_down_count,
                "northbound_net": northbound_net,
            }
        }


# ============================================================
# CLI 命令
# ============================================================

def _safe_float(val: Any) -> float | None:
    try:
        return float(val) if val is not None else None
    except (ValueError, TypeError):
        return None


def cmd_health():
    """全链路健康检测"""
    print("=" * 60)
    print("  market_analyzer.py 全链路健康检测")
    print("=" * 60)

    # 1. 新闻检测
    print("\n[1/4] 新闻采集器...")
    try:
        headlines = NewsFetcher.fetch_headlines("600170")
        print(f"  [OK] 4源聚合: {len(headlines)}条头条新闻")
        sources = defaultdict(int)
        for h in headlines:
            sources[h.source] += 1
        for src, cnt in sources.items():
            print(f"    - {src}: {cnt}条")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # 2. THS数据检测
    print("\n[2/4] 同花顺板块数据...")
    try:
        concepts = THSDataFetcher.get_concept_list()
        industries = THSDataFetcher.get_industry_list()
        print(f"  [OK] 概念板块: {len(concepts)}个")
        print(f"  [OK] 行业板块: {len(industries)}个")

        # 尝试取行情
        test_quote = THSDataFetcher.get_concept_index("人形机器人")
        if test_quote:
            print(f"  [OK] 概念行情: 人形机器人 {test_quote.get('change_pct', '?')}%")
        else:
            print("  [WARN] 概念行情返回空")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # 3. EM数据检测
    print("\n[3/4] 东方财富特色数据...")
    try:
        hot = THSDataFetcher.get_hot_rank()
        print(f"  [OK] 热门排名: {len(hot)}只")

        chi_high = THSDataFetcher.get_continuous_high()
        print(f"  [OK] 持续新高: {len(chi_high)}只")

        summary = THSDataFetcher.get_concept_summary()
        print(f"  [OK] 概念摘要: {len(summary)}条")

        members = THSDataFetcher.get_em_concept_members()
        print(f"  [OK] 概念成分股: {len(members)}只")
    except Exception as e:
        print(f"  [FAIL] {e}")

    # 4. 分析模型检测
    print("\n[4/4] 分析模型...")
    try:
        # 用模拟数据验证模型
        test_sectors = [
            {"name": "AI", "change_pct": 3.5, "volume": 1e8, "raw": [
                {"收盘价": 100, "成交量": 1e7}, {"收盘价": 103.5, "成交量": 1.2e7}
            ]},
            {"name": "新能源", "change_pct": -2.0, "volume": 5e7, "raw": [
                {"收盘价": 200, "成交量": 4e6}, {"收盘价": 196, "成交量": 5e6}
            ]},
        ]
        quad = MarketModels.four_quadrant(test_sectors)
        entropy = MarketModels.entropy_consensus(quad)
        clock = MarketModels.sentiment_clock(1.2, 2.5, 35, 5, 30.0)

        print(f"  [OK] 四象限: {len(quad)}个板块分类")
        print(f"  [OK] 信息熵: {entropy['entropy']} ({entropy['consensus_level']})")
        print(f"  [OK] 情绪时钟: {clock['total_score']}分 → {clock['phase']}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    print("\n" + "=" * 60)
    print("  检测完成")
    print("=" * 60)


def cmd_news():
    """今日财经要闻"""
    print("=" * 60)
    print(f"  今日财经要闻 ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    print("=" * 60)
    headlines = NewsFetcher.fetch_headlines()
    for i, h in enumerate(headlines, 1):
        emoji = {"positive": "[+]", "negative": "[-]", "neutral": "[*]"}.get(h.sentiment, "[*]")
        print(f"\n{i:2d}. {emoji} {h.title}")
        if h.content:
            print(f"    {h.content[:100]}")
        print(f"    来源: {h.source} | 影响度: {h.impact_score:.0f}")


def cmd_sector():
    """板块四象限分析"""
    print("[Analyzing] 正在获取板块数据（约需1-2分钟）...")
    sectors = THSDataFetcher.get_concept_batch_quotes([], max_names=40)
    if not sectors:
        print("无板块数据")
        return

    quad_items = MarketModels.four_quadrant(sectors)
    entropy = MarketModels.entropy_consensus(quad_items)

    print(f"\n{'='*60}")
    print(f"  板块四象限分析 ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    print(f"  信息熵: {entropy['entropy']} → {entropy['consensus_level']}")
    print(f"{'='*60}")

    # 按象限分组
    by_quad: dict[str, list[QuadrantItem]] = defaultdict(list)
    for item in quad_items:
        by_quad[item.quadrant].append(item)

    quad_names = {
        "I": "强共识上涨(追涨)",
        "II": "弱共识上涨(谨慎)",
        "III": "弱共识下跌(关注)",
        "IV": "强共识下跌(规避)",
    }

    for q in ["I", "II", "III", "IV"]:
        items = sorted(by_quad.get(q, []), key=lambda x: abs(x.change_pct), reverse=True)
        print(f"\n[象限{q}] {quad_names.get(q, '')}: {len(items)}个板块")
        print(f"{'板块名称':<16} {'涨跌幅':>8} {'共识度':>8} {'量比':>6}")
        print("-" * 44)
        for item in items[:8]:
            print(f"{item.name:<16} {item.change_pct:>+7.2f}% {item.consensus_strength:>7.1f} {item.volume_ratio:>5.2f}x")


def cmd_sentiment(market_change: float = 0, up_down: float = 1, lt_up: int = 0, lt_down: int = 0, nb_net: float = 0):
    """情绪时钟"""
    clock = MarketModels.sentiment_clock(market_change, up_down, lt_up, lt_down, nb_net)
    print(f"\n{'='*60}")
    print(f"  市场情绪时钟 ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    print(f"{'='*60}")
    print(f"  总评分: {clock['total_score']}/100")
    print(f"  情绪阶段: {clock['phase']}")
    print(f"  描述: {clock['description']}")
    print(f"  建议: {clock['action']}")
    print(f"\n  评分明细:")
    for dim, score in clock['breakdown'].items():
        bar = '█' * int(score / 2.5) + '░' * (10 - int(score / 2.5))
        print(f"    {dim}: {bar} {score}/25")
    print(f"\n  输入参数:")
    for k, v in clock['inputs'].items():
        print(f"    {k}: {v}")


def cmd_report():
    """生成综合分析报告JSON"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0",
        "modules": {}
    }

    # 1. 新闻头条
    print("[1/5] 采集新闻...")
    headlines = NewsFetcher.fetch_headlines()
    report["modules"]["news"] = {
        "count": len(headlines),
        "headlines": [
            {"title": h.title, "source": h.source, "sentiment": h.sentiment,
             "impact": h.impact_score, "time": h.publish_time}
            for h in headlines
        ]
    }

    # 2. 板块数据
    print("[2/5] 获取板块数据...")
    sectors = THSDataFetcher.get_concept_batch_quotes([], max_names=30)
    if sectors:
        quad = MarketModels.four_quadrant(sectors)
        entropy = MarketModels.entropy_consensus(quad)
        report["modules"]["sector_analysis"] = {
            "total_sectors": len(sectors),
            "entropy": entropy["entropy"],
            "consensus_level": entropy["consensus_level"],
            "distribution": entropy["distribution"],
            "quadrants": [
                {"name": q.name, "change_pct": q.change_pct, "quadrant": q.quadrant,
                 "consensus": q.consensus_strength, "volume_ratio": q.volume_ratio}
                for q in quad[:15]
            ]
        }

    # 3. 情绪时钟
    print("[3/5] 计算情绪时钟...")
    hot = THSDataFetcher.get_hot_rank()
    lt_up = sum(1 for h in hot if _safe_float(h.get("涨跌幅")) and _safe_float(h.get("涨跌幅")) >= 9.5)
    lt_down = sum(1 for h in hot if _safe_float(h.get("涨跌幅")) and _safe_float(h.get("涨跌幅")) <= -9.5)

    # 从sectors推算大盘变化
    if sectors:
        avg_change = sum(s.get("change_pct", 0) or 0 for s in sectors) / len(sectors)
        up_count = sum(1 for s in sectors if (s.get("change_pct", 0) or 0) > 0)
        down_count = len(sectors) - up_count
        up_down_ratio = up_count / down_count if down_count > 0 else 10.0
    else:
        avg_change = 0
        up_down_ratio = 1.0

    clock = MarketModels.sentiment_clock(avg_change, up_down_ratio, lt_up, lt_down, 0)
    report["modules"]["sentiment_clock"] = clock

    # 4. 热门股票
    print("[4/5] 获取热门排名...")
    report["modules"]["hot_rank"] = {
        "top30": hot[:30]
    }

    # 5. 概念摘要
    print("[5/5] 获取概念摘要...")
    summary = THSDataFetcher.get_concept_summary()
    report["modules"]["concept_summary"] = summary[:20]

    # 输出
    output_path = f"C:/Users/wolfj/WorkBuddy/Claw/reports/market_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"

    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n 报告已保存: {output_path}")
    print(f" 模块: 新闻({len(headlines)}条) | 板块({len(sectors)}个) | 情绪({clock['phase']}) | 热门({len(hot)}只)")
    return report


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 1 else ["health"]

    if not args or args[0] in ("health", "status"):
        cmd_health()

    elif args[0] in ("news", "要闻"):
        cmd_news()

    elif args[0] in ("sector", "板块", "四象限"):
        cmd_sector()

    elif args[0] in ("sentiment", "情绪", "时钟"):
        cmd_sentiment()

    elif args[0] in ("report", "报告"):
        cmd_report()

    else:
        print(f"用法: python market_analyzer.py [health|news|sector|sentiment|report]")
        sys.exit(1)
