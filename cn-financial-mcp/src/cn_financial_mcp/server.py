"""
cn-financial-mcp: China Financial Data MCP Server based on AKShare.

Provides free financial data for Chinese mainland market via MCP protocol.
Supports stdio (dev) and HTTP/SSE (production) transport modes.
"""

from mcp.server.fastmcp import FastMCP

# Create the MCP server instance
mcp = FastMCP(
    name="cn-financial-mcp",
    instructions=(
        "cn-financial-mcp provides free Chinese mainland financial data via AKShare. "
        "Use the available tools to search stocks, get real-time quotes, historical prices, "
        "financial statements, valuation metrics, industry data, market overview, news, "
        "and macroeconomic indicators. All stock codes should be 6-digit A-share codes "
        "(e.g., '000001' for Ping An Bank, '600519' for Kweichow Moutai)."
    ),
)


def register_all_tools():
    """Register all tool modules with the MCP server."""
    # V0.1: Company info + Price data
    from .tools.company_info import register as reg_company
    from .tools.price_data import register as reg_price

    reg_company(mcp)
    reg_price(mcp)

    # V0.2: Financial statements + Valuation
    from .tools.financial_stmt import register as reg_financial
    from .tools.valuation import register as reg_valuation

    reg_financial(mcp)
    reg_valuation(mcp)

    # V0.3: Industry + Market + News
    from .tools.industry import register as reg_industry
    from .tools.market import register as reg_market
    from .tools.news_events import register as reg_news

    reg_industry(mcp)
    reg_market(mcp)
    reg_news(mcp)

    # V0.4: Macro & FX
    from .tools.macro_fx import register as reg_macro

    reg_macro(mcp)


# Register all tools at import time
register_all_tools()
