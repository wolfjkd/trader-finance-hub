"""
signal_data.py MCP 工具注册测试。
"""

import pytest
import ast


class TestSignalDataSyntax:
    """验证 signal_data.py 语法正确。"""

    def test_parse_ok(self):
        with open(
            r"C:\Users\wolfj\WorkBuddy\Claw\trader-finance-hub\cn-financial-mcp\src\cn_financial_mcp\tools\signal_data.py",
            "r", encoding="utf-8",
        ) as f:
            source = f.read()
        tree = ast.parse(source)
        assert tree is not None

    def test_has_14_tools(self):
        """signal_data.py 注册了 14 个 MCP 工具。"""
        with open(
            r"C:\Users\wolfj\WorkBuddy\Claw\trader-finance-hub\cn-financial-mcp\src\cn_financial_mcp\tools\signal_data.py",
            "r", encoding="utf-8",
        ) as f:
            source = f.read()
        count = source.count("@mcp.tool()")
        assert count == 14, f"Expected 14 @mcp.tool(), got {count}"
