# 金融数据中枢 - 架构设计文档

## 1. 系统概览

Buddy 金融数据中枢是一个多源 MCP 数据聚合平台，为 AI Agent 提供统一的中国金融市场数据接口。

## 2. 核心组件

### 2.1 MCP 协议层
- **协议**: Model Context Protocol (MCP)
- **传输**: stdio (本地) / HTTP-SSE (远程)
- **格式**: JSON-RPC 2.0

### 2.2 数据源

| 数据源 | 接入方式 | 优先级 | 用途 |
|--------|----------|--------|------|
| 腾讯接口 | HTTP 直连 | P0 | 实时行情快照 |
| 通达信 MCP | MCP stdio | P0 | 行情/K线/公告/研报 |
| Wind MCP | CLI + MCP | P1 | 深度财务/技术指标 |
| 东财 MCP | MCP stdio | P1 | 行业/板块/宏观 |
| ftshare | CLI | P2 | 公告PDF下载 |
| WebSearch | AI内置 | P3 | 新闻兜底 |

### 2.3 智能路由 (data_router.py)

```
请求 → probe_sources(数据类型)
    │
    ├── ThreadPoolExecutor 并行探测
    │     ├── TencentAdapter  (行情/指数)
    │     ├── WindAdapter      (深度数据)
    │     ├── EastMoneyAdapter (行业/板块/宏观)
    │     └── FtShareAdapter   (公告)
    │
    ↓
select_best(results) → 评分择优
```

评分模型: 可用性40% + 及时性30% + 质量30%

### 2.4 本地知识库 (Phase 2)
- SQLite 存储研报/公告
- 语义搜索
- 定时自动缓存

## 3. 数据流

```
定时任务触发
    ↓
data_router.py health → 检测存活数据源
    ↓
并行获取数据 (行情/公告/新闻/财务)
    ↓
本地缓存 (可选)
    ↓
生成报告 → 腾讯文档
```

## 4. 扩展性设计

### 新增数据源
1. 实现 Adapter 接口 (probe + fetch)
2. 在 `data_router.py` 注册
3. 配置评分权重

### 切换数据源
- 自动: 健康检测 <50分自动降级
- 手动: 修改 `config/mcp-servers.json`

## 5. 部署环境

| 组件 | 位置 | 说明 |
|------|------|------|
| WorkBuddy | `~/.workbuddy/` | AI Agent 主体 |
| MCP Config | `~/.workbuddy/.mcp.json` | MCP Server 注册 |
| 项目代码 | `~/.workbuddy/skills/wolfjkd-trader-data/` | 智能路由+Skill |
| 东财 MCP | `buddy-finance-hub/cn-financial-mcp/` | 新增数据源 |
| Wind MCP | `~/.workbuddy/skills/wind-mcp-skill/` | Wind 金融数据 |
| ftshare | `~/.workbuddy/skills/ftshare-announcement-data/` | 公告数据 |
