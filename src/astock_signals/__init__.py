"""
astock_signals — A-stock signal data modules for trader-finance-hub.

TradingAgents-astock 移植层。提供以下核心能力:
  - anti_ban_client:  东财防封客户端（节流+Session复用）
  - lockup:           限售解禁日历（RPT_LIFT_STAGE）
  - hot_money:        涨停归因/热点资金追踪（同花顺 editorial）
  - concept:          概念板块归属（东财+百度PAE fallback）
  - indicators:       技术指标计算（MACD/RSI/Boll/ATR 等）

V0.1 — 从 TradingAgents-astock 移植。
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
]

__version__ = "0.1.0"
