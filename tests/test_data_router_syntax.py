"""
data_router.py 语法和命令注册测试。
"""

import pytest
import ast


class TestDataRouterSyntax:
    """验证 data_router.py 语法正确，命令数量完整。"""

    def _parse_router(self):
        path = r"C:\Users\wolfj\.workbuddy\skills\trader-data-router\data_router.py"
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        return ast.parse(source), source

    def test_syntax_valid(self):
        tree, _ = self._parse_router()
        assert tree is not None

    def test_has_17_cmd_functions(self):
        """data_router.py 应有 17 个 cmd_ 函数（含新增的 etf/cb/tickstore）。"""
        tree, source = self._parse_router()
        cmd_funcs = [
            n.name for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.name.startswith("cmd_")
        ]
        assert len(cmd_funcs) == 17, f"Expected 17 cmd_ functions, got {len(cmd_funcs)}: {cmd_funcs}"

    def test_main_entry_has_all_commands(self):
        """main() 应路由所有 17 个命令。"""
        _, source = self._parse_router()
        expected_commands = [
            "health", "quote", "watchlist", "compare",
            "kline", "minute", "auction", "tick", "f10",
            "fundflow", "northbound", "dragon", "concept", "industry",
            "etf", "cb", "tickstore",
        ]
        for cmd in expected_commands:
            assert f'"{cmd}"' in source or f"'{cmd}'" in source, f"Command '{cmd}' not found in main()"
