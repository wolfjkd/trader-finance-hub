"""
Shared test fixtures for cn-financial-mcp tests.
"""

import sys
from pathlib import Path

import pytest

# Add src to path so tests can import cn_financial_mcp
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_symbols():
    """Common test stock symbols."""
    return {
        "pingan": "000001",      # 平安银行 (Shenzhen main)
        "moutai": "600519",      # 贵州茅台 (Shanghai main)
        "catl": "300750",        # 宁德时代 (ChiNext)
        "smic": "688981",        # 中芯国际 (STAR)
    }


@pytest.fixture
def mcp_server():
    """Get the MCP server instance with all tools registered."""
    from cn_financial_mcp.server import mcp
    return mcp
