# Trader Finance Hub

<p align="center">
  <strong>AI金融数据聚合平台</strong><br/>
  AKShare 封装 · eltdx 通达信协议 · 本地 MCP Server · 47 个工具
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13+-blue.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/MCP-1.0-green.svg" alt="MCP"/>
  <img src="https://img.shields.io/badge/License-Apache--2.0-yellow.svg" alt="License"/>
  <img src="https://img.shields.io/badge/Data-A股-red.svg" alt="Data Scope"/>
  <img src="https://img.shields.io/badge/Tools-47-orange.svg" alt="MCP Tools"/>
</p>

---

## 项目定位

为 AI Agent（WorkBuddy / Claude Code / Cursor）提供 **A 股金融数据的 MCP 接口**。

**当前数据源**：
- **AKShare**：42 个金融工具（财务/估值/行业/新闻/宏观）
- **eltdx 1.0.2**：5 个通达信独有工具（集合竞价/逐笔/F10/分时/K线）

**不吹牛**：这不是"多源智能路由"，就是两个数据源的 MCP 壳。  
多源聚合是规划目标，代码里还没实现。

---

## 实际架构

```
AI Agent (WorkBuddy)
        │
        ▼
  cn-financial-mcp (stdio MCP)
        │
        ├── AKShare 封装（42 工具）
        │     └─ 东财/新浪/腾讯后端
        │
        └── eltdx 1.0.2 封装（5 工具）
              └─ 通达信私有协议
```

**与 WorkBuddy 其他数据源的关系**：

| 数据源 | 通道 | 本项目是否包含 |
|--------|------|---------------|
| cn-financial-mcp | mcp.json | ✅ 本项目 |
| 通达信 connector (tdx-connector) | WorkBuddy connector | ❌ 外部，WorkBuddy 内置 |
| Wind (wind-mcp-skill) | WorkBuddy skill | ❌ 外部，需 API Key |

---

## MCP 工具清单（47 个）

### AKShare 封装（42 个）

| 类别 | 工具数 | 覆盖 |
|------|--------|------|
| 公司信息 | 4 | 搜索/概况/竞品 |
| 行情数据 | 4 | 实时/历史K线/市值/列表 |
| 财务报表 | 8 | 三表+指标+增长率+每股 |
| 估值分析 | 4 | PE/PB/分红/机构持仓/评级 |
| 行业板块 | 5 | 板块/成分股/概念/资金流 |
| 市场总览 | 5 | 指数/资金流/北向/涨跌停/龙虎榜 |
| 新闻公告 | 4 | 新闻/日历/公告/搜索 |
| 宏观衍生 | 8 | GDP/CPI/PMI/M2/汇率/国债/两融 |

### eltdx 独有（5 个）

| 工具 | 延迟 | AKShare 是否有 |
|------|------|---------------|
| `eltdx_get_auction` 集合竞价 | ~40ms | ❌ 没有 |
| `eltdx_get_ticks` 逐笔成交 | ~45ms | ❌ 没有 |
| `eltdx_get_f10` F10资料（含题材归因） | ~2200ms | ❌ 没有 |
| `eltdx_get_minutes` 分时 | ~40ms | ⚠️ 有但源不同 |
| `eltdx_get_kline` K线 | ~80ms | ⚠️ 有但源不同 |

---

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/wolfjkd/trader-finance-hub.git
cd trader-finance-hub
```

### 2. 创建独立 venv（推荐）

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

### 3. 安装 cn-financial-mcp

```bash
cd cn-financial-mcp
pip install hatchling editables
pip install --no-build-isolation -e .
```

### 4. 安装运行时依赖

```bash
pip install akshare mcp pandas pydantic eltdx
```

---

## 配置到 WorkBuddy

编辑 `~/.workbuddy/mcp.json`：

```json
{
  "mcpServers": {
    "cn-financial-mcp": {
      "command": "/path/to/venv/Scripts/python.exe",
      "args": ["-m", "cn_financial_mcp"],
      "env": {}
    }
  }
}
```

保存后重启 WorkBuddy，连接器页面 `cn-financial-mcp` 应显示绿色。

---

## 验证

重启后在对话里测试：

```
查中国能建（601868）K线
```

AI 会调用 `mcp__cn-financial-mcp__eltdx_get_kline`，返回 100 根日 K 线。

---

## 已知限制

1. **eltdx 逐笔数据不带时间字段**（`time: null`），只有价格/量/方向
2. **eltdx F10 延迟高**（~2 秒），但数据独有（题材归因是 AKShare 没有的）
3. **没有智能路由**：每个工具写死一个数据源，不会自动择优
4. **Wind/通达信 MCP 不在本项目里**：通过 WorkBuddy connector/skill 系统接入

---

## 版本历史

| 版本 | 日期 | 内容 |
|------|------|------|
| v2.1.0 | 2026-06-22 | 新增 A 股信号数据模块：涨停归因/解禁日历/概念归属/一致预期/技术指标，6 个新 MCP 工具，53 工具就绪 |
| v2.0.1 | 2026-06-17 | 集成 eltdx 5 个工具；修复 pyproject.toml hatchling 配置；47 工具全跑通 |
| v2.0.0 | 2026-06-04 | eltdx 通达信协议集成（原 `eltdx_provider.py`） |
| v1.0.0 | 2026-06-02 | 全市场综合分析引擎 |
| v0.1.0 | 2026-06-01 | 项目初始化；集成 cn-financial-mcp |

---

## 许可

Apache-2.0 License

---

## 作者

**郭良勇 (wolfjkd)** — A股T0日内交易员
