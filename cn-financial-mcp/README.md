# cn-financial-mcp

<p align="center">
  <strong>cn大陆金融数据 MCP Server</strong><br/>
  基于 <a href="https://akshare.akfamily.xyz">AKShare</a> · 支持 <a href="https://modelcontextprotocol.io">MCP 协议</a> · 42 个金融工具
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/MCP-1.0-green.svg" alt="MCP 1.0"/>
  <img src="https://img.shields.io/badge/License-Apache--2.0-yellow.svg" alt="Apache-2.0 License"/>
  <img src="https://img.shields.io/badge/Data-A%E8%82%A1%20%7C%20%E5%AE%8F%E8%A7%82%20%7C%20%E8%A1%8C%E4%B8%9A-red.svg" alt="A股 | 宏观 | 行业"/>
</p>

---

## 📸 Demo

> 在 Claude Code 中通过 MCP 工具查询中国西电的盘口走势以及投研分析

<p align="center">
  <img src="docs/images/demo-query.png" width="600" alt="查询示例"/>
</p>

<p align="center">
  <img src="docs/images/demo-result.png" width="600" alt="返回结果"/>
</p>

---

## 简介

**cn-financial-mcp** 是一个遵循 [Model Context Protocol (MCP)](https://modelcontextprotocol.io) 标准的金融数据服务器，专注于cn大陆市场。它让任何支持 MCP 的 AI Agent（如 Claude Code、Cursor、自定义 Agent）都能直接调用 A 股行情、财报、行业、宏观经济等 **42 个金融工具**，无需 API Key，开箱即用。

底层数据来源于 [AKShare](https://akshare.akfamily.xyz)，并内置多数据源自动 fallback 机制（东方财富 → 新浪 / 腾讯 / 同花顺），确保在不同网络环境下的可用性。

---

## ✨ 功能一览

| 模块 | 工具数 | 说明 |
|:-----|:------:|:-----|
| **公司信息** | 4 | 股票搜索、公司概况、主营构成、竞争对手 |
| **行情数据** | 4 | 实时行情、历史 K 线（日/周/月）、市值、股票列表 |
| **财务报表** | 8 | 利润表、资产负债表、现金流量表、财务指标、增长率、分部收入 |
| **估值分析** | 4 | PE/PB/PS 时序、分红历史、机构持仓、分析师评级 |
| **行业板块** | 5 | 行业列表、成分股、概念板块、板块资金流、行业估值 |
| **市场总览** | 5 | 指数概览、个股资金流、北向资金、涨跌停池、龙虎榜 |
| **新闻公告** | 4 | 个股新闻、财报日历、公司公告、关键词搜索 |
| **宏观与衍生** | 8 | GDP/CPI/PMI/M2、汇率、国债收益率、融资融券、高管增减持 |

**合计 42 个工具**，覆盖从个股研究到宏观分析的完整链路。

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- pip

### 安装

```bash
git clone https://github.com/<your-username>/cn-financial-mcp.git
cd cn-financial-mcp
pip install -e .
```

### 验证安装

```bash
PYTHONPATH=src python -m cn_financial_mcp --help
```

```
usage: __main__.py [-h] [--http] [--port PORT] [--host HOST]

cn-financial-mcp: China Financial Data MCP Server based on AKShare

options:
  -h, --help   show this help message and exit
  --http       Run in HTTP/SSE mode instead of stdio
  --port PORT  Port for HTTP/SSE mode (default: 8000)
  --host HOST  Host for HTTP/SSE mode (default: 127.0.0.1)
```

---

## 📡 部署方式

### 方式一：stdio 模式（Claude Code / Cursor）

在你的项目根目录 `.mcp.json` 中添加：

```json
{
  "mcpServers": {
    "cn-financial": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "cn_financial_mcp"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/cn-financial-mcp/src"
      }
    }
  }
}
```

> 将 `/absolute/path/to/cn-financial-mcp` 替换为你的实际路径。配置好后 Agent 会自动拉起 MCP 进程。

### 方式二：HTTP/SSE 模式（通用 MCP Client）

```bash
cd cn-financial-mcp
PYTHONPATH=src python -m cn_financial_mcp --http --host 0.0.0.0 --port 8000
```

MCP Client 连接 endpoint：

```
http://<your-ip>:8000/sse
```

### 方式三：Docker

```bash
cd cn-financial-mcp
docker compose up -d
```

服务暴露在 `http://localhost:8000`。

---

## 🛠 工具清单

<details>
<summary><b>公司信息 (company_info)</b></summary>

| 工具 | 说明 |
|:-----|:-----|
| `search_stock` | 按名称/代码模糊搜索 A 股 |
| `get_company_info` | 获取公司基本信息（行业、市值、股本） |
| `get_company_profile` | 获取主营业务构成及收入占比 |
| `get_competitors` | 获取同行业竞争对手列表 |

</details>

<details>
<summary><b>行情数据 (price_data)</b></summary>

| 工具 | 说明 |
|:-----|:-----|
| `get_realtime_quote` | 获取实时行情（最新价、涨跌幅、成交量） |
| `get_historical_price` | 获取历史 K 线（日/周/月，支持前复权/后复权） |
| `get_market_capitalization` | 获取总市值与流通市值 |
| `get_stock_list` | 获取 A 股完整列表，支持市值筛选 |

</details>

<details>
<summary><b>财务报表 (financial_stmt)</b></summary>

| 工具 | 说明 |
|:-----|:-----|
| `get_income_statement` | 利润表 |
| `get_balance_sheet` | 资产负债表 |
| `get_cash_flow_statement` | 现金流量表 |
| `get_financial_line_item` | 自定义查询单项科目 |
| `get_financial_indicators` | 综合财务指标（ROE、毛利率等） |
| `get_growth_rates` | 营收/利润增长率 |
| `get_per_share_data` | 每股指标（EPS、BPS等） |
| `get_segments_revenue` | 分部收入明细 |

</details>

<details>
<summary><b>估值分析 (valuation)</b></summary>

| 工具 | 说明 |
|:-----|:-----|
| `get_valuation_metrics` | PE/PB/PS 历史时序 |
| `get_dividend_data` | 分红派息历史 |
| `get_institutional_holdings` | 十大流通股东 |
| `get_analyst_rating` | 分析师评级与盈利预测 |

</details>

<details>
<summary><b>行业板块 (industry)</b></summary>

| 工具 | 说明 |
|:-----|:-----|
| `get_industry_list` | 行业板块列表 |
| `get_industry_stocks` | 行业成分股 |
| `get_concept_list` | 概念板块列表 |
| `get_sector_fund_flow` | 板块资金流向排名 |
| `get_industry_pe` | 行业历史行情走势 |

</details>

<details>
<summary><b>市场总览 (market)</b></summary>

| 工具 | 说明 |
|:-----|:-----|
| `get_market_overview` | 主要指数实时快照 |
| `get_money_flow` | 个股资金流向 |
| `get_north_bound_flow` | 北向资金（沪深港通）净流入 |
| `get_limit_up_down` | 当日涨停/跌停池 |
| `get_dragon_tiger` | 龙虎榜（机构活跃交易） |

</details>

<details>
<summary><b>新闻公告 (news_events)</b></summary>

| 工具 | 说明 |
|:-----|:-----|
| `get_stock_news` | 个股新闻资讯 |
| `get_financial_calendar` | 财报披露时间表 |
| `get_company_announcements` | 上市公司公告 |
| `search_news` | 按关键词搜索新闻 |

</details>

<details>
<summary><b>宏观与衍生 (macro_fx)</b></summary>

| 工具 | 说明 |
|:-----|:-----|
| `get_macro_gdp` | GDP 数据 |
| `get_macro_cpi` | CPI 数据 |
| `get_macro_pmi` | PMI 数据 |
| `get_macro_money_supply` | 货币供应量（M0/M1/M2） |
| `get_fx_rate` | 汇率查询 |
| `get_bond_yield_curve` | 国债收益率曲线 |
| `get_margin_trading` | 融资融券数据 |
| `get_insider_trading` | 高管增减持 |

</details>

---

## 🔄 多数据源 Fallback

为应对部分数据源在云服务器环境下不稳定的问题，内置了自动多源切换：

```
请求 → 东方财富 (优先，字段最全)
         ↓ 失败
       新浪 / 腾讯 / 同花顺 (备选)
         ↓ 失败
       返回错误
```

| 功能 | 主源 | 备选源 |
|:-----|:----:|:------:|
| 实时行情 | 东方财富 | 新浪 → 新浪单股 |
| 历史 K 线 | 东方财富 | 腾讯 |
| 行业板块 | 东方财富 | 同花顺 |
| 概念板块 | 东方财富 | 同花顺 |
| 公司信息 | 东方财富 emweb | 新浪 |

> 代码始终优先尝试东方财富。只有当主源连接失败时才自动切换，对调用方完全透明。

---

## 🧪 测试

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行单元测试
pytest tests/ -v

# 仅运行网络无关测试
pytest tests/ -v -m "not network"
```

---

## 📁 项目结构

```
cn-financial-mcp/
├── src/cn_financial_mcp/
│   ├── __init__.py
│   ├── __main__.py          # CLI 入口
│   ├── server.py             # MCP Server 实例
│   ├── tools/
│   │   ├── company_info.py   # 公司信息 (4 tools)
│   │   ├── price_data.py     # 行情数据 (4 tools)
│   │   ├── financial_stmt.py # 财务报表 (8 tools)
│   │   ├── valuation.py      # 估值分析 (4 tools)
│   │   ├── industry.py       # 行业板块 (5 tools)
│   │   ├── market.py         # 市场总览 (5 tools)
│   │   ├── news_events.py    # 新闻公告 (4 tools)
│   │   └── macro_fx.py       # 宏观衍生 (8 tools)
│   └── utils/
│       ├── cache.py          # TTL 缓存
│       ├── fallback.py       # 多源 fallback
│       ├── formatter.py      # DataFrame → JSON
│       └── symbol.py         # 股票代码工具
├── tests/
├── docs/images/
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── .mcp.json
```

---

## 📄 License

[Apache-2.0](LICENSE)

---

## 🙏 致谢

- [AKShare](https://akshare.akfamily.xyz) — 开源金融数据接口库
