# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/lang/zh-CN/).

## [2.1.0] - 2026-06-22

### Added
- 新增 `astock_signals/` 信号数据模块（5个文件），移植自 TradingAgents-astock 项目
- `anti_ban_client.py` — 东方财富 HTTP 防封限流客户端（Session 复用 + 串行限流 + 随机抖动）
- `hot_money.py` — 涨停归因接口（同花顺 editorial，含主题频次统计）
- `lockup.py` — 限售解禁日历接口（东财 datacenter RPT_LIFT_STAGE，含风险提示）
- `concept.py` — 个股概念/行业/地域板块归属（push2delay 镜像 + 地域板块反查策略）
- `indicators.py` — 13种技术指标计算（MACD/RSI/Boll/ATR/KDJ/MFI 等，stockstats 引擎）
- 新增 6 个 MCP 工具：`get_hot_stocks` / `get_lockup_expiry` / `get_concept_attribution` / `get_profit_forecast` / `get_technical_indicator` / `list_technical_indicators`
- `get_profit_forecast` 支持分析师一致预期 EPS + Forward PE + PEG + PE 消化年限

### Changed
- `server.py` 注册 signal_data 工具模块（53 工具全部就绪）
- 清理 `server.py` 中误导性的 V0.x 内部注释，改为中文功能描述

### Fixed
- `get_profit_forecast` 从 `pd.read_html`（JS 渲染 SPA 解析失败）改为正则精准匹配 `<thead>/<tbody>`

## [2.0.0] - 2026-06-01

### Added
- 集成eltdx通达信行情协议，提供独有数据源
- 新增集合竞价数据接口（开盘前竞价撮合详情）
- 新增逐笔成交数据接口（每笔成交明细）
- 新增F10资料数据接口（公司概况/热点题材/财务诊断）
- 新增开盘前分析模块（基于集合竞价数据预判热点板块）
- 新增资金流向分析模块（基于逐笔成交识别主力资金动向）
- 新增个股筛选模块（基于F10资料快速筛选投资价值）
- 更新数据源矩阵，新增eltdx独有数据源对比表
- 更新CLI命令，新增eltdx独有数据分析命令

### Changed
- 优化智能路由策略，独有数据类型（竞价/逐笔/F10）固定使用eltdx
- 更新数据源评分模型，考虑独有数据源的不可替代性
- 完善项目文档，添加eltdx独有数据源说明

### Technical Details
- eltdx集成版本：1.0.2
- eltdx许可：仅限个人学习、协议研究和非商业研究使用
- 竞价数据延迟：~114ms
- 逐笔成交延迟：~150ms
- F10资料延迟：~200ms

### Notes
- eltdx提供腾讯接口无法覆盖的独有数据类型
- 独有数据对T0日内交易有重要价值
- 保持对原有数据源（腾讯/Wind/东财）的兼容

## [1.0.0] - 2026-05-01

### Added
- 初始版本发布
- 多源MCP数据聚合平台架构
- 智能路由系统（trader-data-router）
- 本地知识库（SQLite+语义搜索）
- 定时任务系统
- 统一MCP协议层
- 支持通达信MCP、Wind MCP、东财MCP、腾讯接口
- 全市场综合分析引擎（market_analyzer.py）
- 新闻聚合引擎（4源聚合）
- 同花顺数据集成（29个THS函数）
- 分析模型：四象限、信息熵、情绪时钟
- CLI命令行工具
- 完整的项目文档和使用示例
- Apache-2.0开源许可证

### Technical Details
- Python 3.10+兼容
- MCP协议1.0支持
- 数据源覆盖：A股、宏观、行业
- 分析模型：四象限、熵共识、情绪时钟