# Trader Finance Hub

<p align="center">
  <strong>AI金融数据聚合平台</strong><br/>
  多源MCP数据聚合 · 智能路由 · 本地知识库 · 定时任务 · 独有数据源
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/MCP-1.0-green.svg" alt="MCP"/>
  <img src="https://img.shields.io/badge/License-Apache--2.0-yellow.svg" alt="License"/>
  <img src="https://img.shields.io/badge/Data-A股|宏观|行业-red.svg" alt="Data Scope"/>
  <img src="https://img.shields.io/badge/Analysis-四象限|熵共识|情绪时钟-orange.svg" alt="Analysis Models"/>
  <img src="https://img.shields.io/badge/eltdx-通达信协议-green.svg" alt="eltdx"/>
</p>

---

## 版本信息

**当前版本**：v2.0.0

**版本历史**：详见 [CHANGELOG.md](CHANGELOG.md)

**版本号规则**：遵循 [语义化版本控制](https://semver.org/lang/zh-CN/)（Semantic Versioning）
- 主版本号：不兼容的 API 修改
- 次版本号：向下兼容的功能性新增
- 修订号：向下兼容的问题修正

## 项目定位

为 AI Agent（WorkBuddy / Claude Code / Cursor）提供**统一的A股金融数据接口**，聚合多源 MCP 数据服务，通过智能路由自动择优，确保数据的高可用和高质量。

**独有数据源**：集成eltdx通达信行情协议，提供腾讯接口无法覆盖的**集合竞价、逐笔成交、F10资料**等独有数据。

---

## 架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI Agent (WorkBuddy)                              │
├─────────────────────────────────────────────────────────────────────────┤
│                        统一 MCP 协议层                                    │
├──────────┬──────────┬──────────┬──────────┬──────────┬────────────────┤
│ 通达信MCP│ Wind MCP │ 东财 MCP │ 腾讯接口  │ eltdx    │ 本地知识库      │
│ 行情/K线  │ 深度财务  │ 42工具    │ 实时快照  │ 独有数据  │ SQLite+语义    │
│ 公告/研报│ 技术指标  │ 财务/宏观 │ 毫秒级    │ 竞价/逐笔 │ 研报缓存       │
├──────────┴──────────┴──────────┴──────────┴──────────┴────────────────┤
│                    trader-data-router 智能路由                            │
│                    多源择优 → 主力源优先 → 缓存 → 统一输出                  │
├─────────────────────────────────────────────────────────────────────────┤
│                    market_analyzer 全市场分析引擎                          │
│   新闻聚合(4源) · 四象限模型 · 信息熵共识度 · 情绪时钟                      │
│   同花顺(THS)板块数据 · eltdx独有数据 · 综合报告生成                        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 数据源矩阵

| 数据源 | 类型 | 工具数 | 覆盖范围 | 状态 |
|--------|------|--------|----------|------|
| **通达信 MCP** (tdx-connector) | MCP | 6大模块 | 行情/公告/研报/新闻/K线/选股 | 运行中 |
| **Wind MCP** (wind-mcp-skill) | MCP + CLI | 8个server | 深度财务/技术指标/板块/宏观 | 运行中 |
| **东方财富 MCP** (cn-financial-mcp) | MCP/HTTP | 4端可用 | 龙虎榜/北向资金/涨停池/Sina日线 | 4/4端点可用 |
| **腾讯接口** | HTTP | - | 实时行情/指数/大宗商品（主力源） | 运行中 |
| **eltdx** | Python | 5个接口 | 集合竞价/逐笔成交/F10资料/分时/K线 | 运行中（独有数据源） |
| **ftshare** | CLI | 公告/研报 | A股公告列表+PDF下载 | 运行中 |

### eltdx独有数据源（v2.0新增）

| 数据类型 | 说明 | 腾讯接口 | eltdx | 延迟 |
|----------|------|---------|-------|------|
| **集合竞价** | 开盘前竞价撮合详情 | ❌ 无 | ✅ 有 | ~114ms |
| **逐笔成交** | 每笔成交明细（时间/价格/量） | ❌ 无 | ✅ 有 | ~150ms |
| **F10资料** | 公司概况/热点题材/财务诊断 | ❌ 无 | ✅ 有 | ~200ms |
| 分时数据 | 分钟级行情 | ✅ 有 | ✅ 有 | ~126ms |
| 行情快照 | 实时价格 | ✅ 有 | ✅ 有 | ~134ms |

### 东财端点可用性（2026-06-01实测）

| 端点 | 状态 | 响应 | 说明 |
|------|------|------|------|
| 龙虎榜 | ✅ | ~600ms | datacenter.eastmoney.com |
| 北向资金 | ✅ | ~1000ms | HSGT历史数据 |
| 涨停池 | ✅ | ~150ms | 当日涨停板 |
| Sina日线行情 | ✅ | ~400ms | `stock_zh_a_daily`（非实时） |
| push2实时行情 | ❌ | - | push2.eastmoney.com 被拒 |
| EM资金流向 | ❌ | - | ConnectionError |
| **WebSearch** | AI | - | 新闻/资讯兜底 | 运行中 |

---

## 全市场综合分析引擎

`src/market_analyzer.py` 提供全套智能化分析能力，可产出"全市场综合分析报告"。

### 新闻聚合引擎
- **4源聚合**: 东财头条 + 巨潮资讯 + 全球财经 + 央视新闻
- **情感检测**: positive / negative / neutral 关键词自动标记
- **影响度评分**: 0-100 分量化新闻对市场的影响程度

### 同花顺数据方案
- 基于 AKShare 内置 29 个 THS 函数，无需 Tushare Pro 高积分
- 覆盖：概念板块行情 / 行业摘要 / 热门排名 / 市场总览

### eltdx独有数据分析（v2.0新增）

| 分析模块 | 数据源 | 功能 | 输出 |
|----------|--------|------|------|
| **开盘前分析** | 集合竞价 | 预判当日热点板块 | 强势/弱势开盘股票列表 |
| **资金流向分析** | 逐笔成交 | 识别主力资金动向 | 大单净流入/流出信号 |
| **个股筛选** | F10资料 | 快速筛选投资价值 | 综合评分+行业/题材/财务 |

### 分析模型

| 模型 | 原理 | 输出 |
|------|------|------|
| **四象限** | 涨幅 x 共识强度 | I(强共识上涨)/II(弱共识上涨)/III(弱共识下跌)/IV(强共识下跌) |
| **信息熵** | 香农熵量化市场分歧 | 高度共识 / 中度共识 / 分歧较大 / 高度分歧 |
| **情绪时钟** | 4维度(涨跌/涨跌比/涨停跌停比/北向)评分 | 绝望/怀疑/希望/乐观/兴奋/贪婪 6阶段 |

### CLI 命令

```bash
python src/market_analyzer.py health      # 数据源健康检测
python src/market_analyzer.py news        # 市场要闻聚合
python src/market_analyzer.py sector      # 板块四象限分析
python src/market_analyzer.py sentiment   # 情绪时钟
python src/market_analyzer.py report      # 全市场综合报告(JSON)

# eltdx独有数据分析（v2.0新增）
python src/market_analyzer.py premarket   # 开盘前分析（集合竞价）
python src/market_analyzer.py flow sz000001  # 资金流向分析（逐笔成交）
python src/market_analyzer.py screen 000001  # 个股筛选（F10资料）
```

---

## 项目结构

```
trader-finance-hub/
├── README.md                 # 说明文档
├── CHANGELOG.md              # 版本变更记录
├── src/
│   ├── __init__.py           # 包初始化，版本信息
│   ├── market_analyzer.py    # 全市场综合分析引擎
│   └── eltdx_provider.py     # eltdx数据源集成
├── cn-financial-mcp/         # 东财MCP服务器
├── config/                   # 配置文件
├── docs/                     # 文档资料
└── scripts/                  # 辅助脚本
```

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/wolfjkd/trader-finance-hub.git
cd trader-finance-hub
```

### 2. 安装东财 MCP

```bash
cd cn-financial-mcp
pip install -e .
```

### 3. 配置 MCP

在 WorkBuddy 的 `.mcp.json` 中添加：

```json
{
  "mcpServers": {
    "cn-financial": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "cn_financial_mcp"],
      "env": {
        "PYTHONPATH": "路径/cn-financial-mcp/src"
      }
    }
  }
}
```

### 4. 安装eltdx（可选，独有数据源）

```bash
pip install eltdx
```

### 5. 验证

```bash
python -c "from cn_financial_mcp.server import mcp; print('东财MCP OK')"
python -c "from eltdx import TdxClient; print('eltdx OK')"
python src/market_analyzer.py health  # 全链路健康检测
```

---

## 数据源对比

### 东财 MCP 核心能力（42个工具）

| 模块 | 工具数 | 关键能力 |
|------|--------|----------|
| 公司信息 | 4 | 搜索/概况/主营/竞品 |
| 行情数据 | 4 | 实时/历史K线/市值/股票列表 |
| 财务报表 | 8 | 三表+指标+增长率+每股数据 |
| 估值分析 | 4 | PE/PB历史/分红/机构持仓/评级 |
| 行业板块 | 5 | 板块列表/成分股/概念/资金流 |
| 市场总览 | 5 | 指数/资金流/北向/涨跌停/龙虎榜 |
| 新闻公告 | 4 | 新闻/日历/公告/搜索 |
| 宏观衍生 | 8 | GDP/CPI/PMI/M2/汇率/国债/两融 |

### 各数据源优劣势

| 场景 | 首选 | 推荐理由 |
|------|------|----------|
| 实时行情快照 | **腾讯接口**【主力】 | 毫秒级响应，无API限制 |
| 集合竞价数据 | **eltdx**【独有】 | 腾讯接口无此功能 |
| 逐笔成交数据 | **eltdx**【独有】 | 腾讯接口无此功能 |
| F10资料数据 | **eltdx**【独有】 | 腾讯接口无此功能 |
| K线历史数据 | Wind MCP | 数据质量最高 |
| 深度财务分析 | Wind MCP | 唯一全字段来源 |
| 公告/研报 | ftshare + 通达信 | PDF下载+自然语言搜索 |
| 行业/板块/宏观 | 东财 MCP | 无API限制，覆盖全 |
| 龙虎榜/北向资金 | 东财 MCP | 唯一稳定来源 |
| 财经新闻 | WebSearch | 实时性最好 |

---

## 项目结构

```
trader-finance-hub/
├── README.md                   # 项目说明
├── cn-financial-mcp/           # 东方财富 MCP Server（子模块）
│   ├── src/cn_financial_mcp/   # 42个金融工具
│   ├── pyproject.toml
│   └── .mcp.json
├── src/                        # 分析引擎
│   ├── market_analyzer.py      # 全市场综合分析引擎（v2.0，含eltdx集成）
│   ├── eltdx_provider.py       # eltdx数据提供者（独有数据源封装）
│   └── __init__.py
├── config/                     # 配置文件
│   └── mcp-servers.json        # MCP Server 配置
├── scripts/                    # 自动化脚本
│   ├── health_check.py         # 数据源健康检测
│   └── daily_report.py         # 每日报告生成
└── docs/                       # 文档
    └── architecture.md         # 架构设计文档
```

---

## 更新日志

| 版本 | 日期 | 内容 |
|------|------|------|
| v2.0.0 | 2026-06-04 | **eltdx通达信协议集成**：新增 eltdx_provider.py（集合竞价/逐笔成交/F10资料3大独有数据源）；market_analyzer.py 新增 EltdxAnalyzer 模块（开盘前分析/资金流向/个股筛选）；全链路健康检测5模块通过 |
| v1.0.0 | 2026-06-02 | 全市场综合分析引擎：NewsFetcher(4源新闻)+THSDataFetcher(同花顺替代)+MarketModels(四象限/熵共识/情绪时钟)；集成到 data_router v3.2 |
| v0.2.0 | 2026-06-01 | 东财适配器重构：切换到 datacenter 端点(龙虎榜/北向/涨停池)+Sina兜底；端点可用性 4/4，评分 82/B |
| v0.1.0 | 2026-06-01 | 项目初始化；集成 cn-financial-mcp (东财42工具)；架构设计 |

---

## 许可

Apache-2.0 License

---

## 作者

**郭良勇 (wolfjkd)** — A股T0日内交易员 & AI金融数据架构师
