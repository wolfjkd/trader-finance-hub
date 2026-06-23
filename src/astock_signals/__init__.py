"""
astock_signals — A-stock signal data modules for trader-finance-hub.

TradingAgents-astock 移植层。提供以下核心能力:
  - anti_ban_client:  东财防封客户端（节流+Session复用）
  - lockup:           限售解禁日历（RPT_LIFT_STAGE）
  - hot_money:        涨停归因/热点资金追踪（同花顺 editorial）
  - concept:          概念板块归属（东财+百度PAE fallback）
  - indicators:       技术指标计算（MACD/RSI/Boll/ATR 等）
  - northbound:       北向资金流向（沪深股通，同花顺 hsgtApi）
  - fund_flow:        个股资金流向（东财 push2）
  - dragon_tiger:     龙虎榜席位明细（东财 datacenter）
  - industry:         行业横向对比（东财 push2 行业排名）

V0.2 — 新增 northbound / fund_flow / dragon_tiger / industry 4 个模块。
"""

from .anti_ban_client import (
    em_get,
    em_datacenter,
    em_push2,
    em_push2_fund_flow,
    em_push2his_fund_flow,
    set_min_interval,
    em_reset_session,
)

from .lockup import get_lockup_expiry, get_lockup_expiry_json
from .hot_money import get_hot_stocks, get_hot_stocks_json
from .concept import get_concept_blocks, get_concept_blocks_json
from .indicators import (
    get_supported_indicators,
    get_indicator_description,
    calculate_indicators,
    get_indicators_text,
)
from .northbound import get_northbound_flow, get_northbound_flow_json
from .fund_flow import get_fund_flow, get_fund_flow_json
from .dragon_tiger import get_dragon_tiger_board, get_dragon_tiger_board_json
from .industry import get_industry_comparison, get_industry_comparison_json

__all__ = [
    # anti_ban_client
    "em_get",
    "em_datacenter",
    "em_push2",
    "em_push2_fund_flow",
    "em_push2his_fund_flow",
    "set_min_interval",
    "em_reset_session",
    # lockup
    "get_lockup_expiry",
    "get_lockup_expiry_json",
    # hot_money
    "get_hot_stocks",
    "get_hot_stocks_json",
    # concept
    "get_concept_blocks",
    "get_concept_blocks_json",
    # indicators
    "get_supported_indicators",
    "get_indicator_description",
    "calculate_indicators",
    "get_indicators_text",
    # northbound
    "get_northbound_flow",
    "get_northbound_flow_json",
    # fund_flow
    "get_fund_flow",
    "get_fund_flow_json",
    # dragon_tiger
    "get_dragon_tiger_board",
    "get_dragon_tiger_board_json",
    # industry
    "get_industry_comparison",
    "get_industry_comparison_json",
]

__version__ = "0.2.0"
