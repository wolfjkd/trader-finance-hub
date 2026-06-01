# Trader Finance Hub

<p align="center">
  <strong>AI金融数据聚合平台</strong><br/>
  多源MCP数据聚合 · 智能路由 · 本地知识库 · 定时任务
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/MCP-1.0-green.svg" alt="MCP"/>
  <img src="https://img.shields.io/badge/License-Apache--2.0-yellow.svg" alt="License"/>
  <img src="https://img.shields.io/badge/Data-A股|宏观|行业-red.svg" alt="Data Scope"/>
  <img src="https://img.shields.io/badge/Analysis-四象限|熵共识|情绪时钟-orange.svg" alt="Analysis Models"/>
</p>

---

## 项目定位

为 AI Agent（WorkBuddy / Claude Code / Cursor）提供**统一的A股金融数据接口**，聚合多源 MCP 数据服务，通过智能路由自动择优，确保数据的高可用和高质量。

---

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent (WorkBuddy)                      │
├─────────────────────────────────────────────────────────────┤
│                    统一 MCP 协议层                            │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ 通达信MCP│ Wind MCP │ 东财 MCP │ 腾讯接口  │ 本地知识库      │
│ 行情/K线  │ 深度财务  │ 42工具    │ 实时快照  │ SQLite+语义    │
│ 公告/研报│ 技术指标  │ 财务/宏观 │ 毫秒级    │ 研报缓存       │
├──────────┴──────────┴──────────┴──────────┴────────────────┤
│              trader-data-router 智能路由                    │
│              多源择优 → 缓存 → 统一输出                       │
├─────────────────────────────────────────────────────────────┤
│              market_analyzer 全市场分析引擎                    │
│   新闻聚合(4源) · 四象限模型 · 信息熵共识度 · 情绪时钟        │
│   同花顺(THS)板块数据 · 综合报告生成                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 数据源矩阵

| 数据源 | 类型 | 工具数 | 覆盖范围 | 状态 |
|--------|------|--------|----------|------|
| **通达信 MCP** (tdx-connector) | MCP | 6大模块 | 行情/公告/研报/新闻/K线/选股 | 运行中 |
| **Wind MCP** (wind-mcp-skill) | MCP + CLI | 8个server | 深度财务/技术指标/板块/宏观 | 运行中 |
| **东方财富 MCP** (cn-financial-mcp) | MCP/HTTP | 4端可用 | 龙虎榜/北向资金/涨停池/Sina日线 | 4/4端点可用 |
| **腾讯接口** | HTTP | - | 实时行情/指数/大宗商品 | 运行中 |
| **ftshare** | CLI | 公告/研报 | A股公告列表+PDF下载 | 运行中 |

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

### 4. 验证

```bash
python -c "from cn_financial_mcp.server import mcp; print('OK')"
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
| 实时行情快照 | 腾讯接口 | 毫秒级响应，无API限制 |
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
│   ├── market_analyzer.py      # 全市场综合分析引擎（618行）
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
| v0.3.0 | 2026-06-01 | 全市场综合分析引擎：NewsFetcher(4源新闻)+THSDataFetcher(同花顺替代)+MarketModels(四象限/熵共识/情绪时钟)；集成到 data_router v3.2 |
| v0.2.0 | 2026-06-01 | 东财适配器重构：切换到 datacenter 端点(龙虎榜/北向/涨停池)+Sina兜底；端点可用性 4/4，评分 82/B |
| v0.1.0 | 2026-06-01 | 项目初始化；集成 cn-financial-mcp (东财42工具)；架构设计 |

---

## 许可

Apache-2.0 License

---

## 作者

**郭良勇 (wolfjkd)** — A股T0日内交易员 & AI金融数据架构师
