"""
可转债数据模块测试。
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from astock_signals.convertible_bond import (
    get_cb_realtime,
    get_cb_value_analysis,
    get_cb_comparison,
    get_cb_info,
)


class TestGetCbRealtime:
    """可转债实时行情测试。"""

    @patch("astock_signals.convertible_bond.ak")
    def test_returns_list(self, mock_ak, sample_cb_df):
        mock_ak.bond_zh_cov.return_value = sample_cb_df
        result = get_cb_realtime(top_n=3)
        assert isinstance(result, list)
        assert len(result) == 3

    @patch("astock_signals.convertible_bond.ak")
    def test_has_required_fields(self, mock_ak, sample_cb_df):
        mock_ak.bond_zh_cov.return_value = sample_cb_df
        result = get_cb_realtime(top_n=1)
        assert "bond_code" in result[0]
        assert "bond_name" in result[0]
        assert "conversion_premium" in result[0]

    @patch("astock_signals.convertible_bond.ak")
    def test_empty_returns_empty(self, mock_ak):
        mock_ak.bond_zh_cov.return_value = pd.DataFrame()
        result = get_cb_realtime()
        assert result == []

    @patch("astock_signals.convertible_bond.ak")
    def test_exception_returns_empty(self, mock_ak):
        mock_ak.bond_zh_cov.side_effect = Exception("network error")
        result = get_cb_realtime()
        assert result == []


class TestGetCbValueAnalysis:
    """可转债价值分析测试。"""

    @patch("astock_signals.convertible_bond.ak")
    def test_returns_list(self, mock_ak):
        df = pd.DataFrame({
            "日期": ["2026-06-24", "2026-06-23"],
            "收盘价": [115.5, 114.0],
            "纯债价值": [95.0, 95.0],
            "转股价值": [106.25, 105.0],
            "纯债溢价率": [21.6, 20.0],
            "转股溢价率": [8.7, 8.6],
        })
        mock_ak.bond_zh_cov_value_analysis.return_value = df
        result = get_cb_value_analysis("113527", days=2)
        assert len(result) == 2
        assert result[0]["date"] == "2026-06-24"

    @patch("astock_signals.convertible_bond.ak")
    def test_exception_returns_empty(self, mock_ak):
        mock_ak.bond_zh_cov_value_analysis.side_effect = Exception("fail")
        result = get_cb_value_analysis("113527")
        assert result == []


class TestGetCbComparison:
    """可转债比价表测试。"""

    @patch("astock_signals.convertible_bond.ak")
    def test_returns_list(self, mock_ak, sample_cb_df):
        # bond_cov_comparison 列名不同，构造专用数据
        df = pd.DataFrame({
            "转债代码": ["113527"],
            "转债名称": ["维格转债"],
            "转债最新价": [115.5],
            "正股代码": ["603518"],
            "正股名称": ["锦泓集团"],
            "转股价": [8.0],
            "转股价值": [106.25],
            "转股溢价率": [8.7],
            "纯债价值": [95.0],
        })
        mock_ak.bond_cov_comparison.return_value = df
        result = get_cb_comparison()
        assert isinstance(result, list)
        assert len(result) == 1

    @patch("astock_signals.convertible_bond.ak")
    def test_exception_returns_empty(self, mock_ak):
        mock_ak.bond_cov_comparison.side_effect = Exception("fail")
        result = get_cb_comparison()
        assert result == []


class TestGetCbInfo:
    """可转债详情测试。"""

    @patch("astock_signals.convertible_bond.ak")
    def test_returns_list(self, mock_ak):
        df = pd.DataFrame({"项目": ["债券代码", "债券简称"], "内容": ["123121", "帝尔转债"]})
        mock_ak.bond_zh_cov_info.return_value = df
        result = get_cb_info("123121")
        assert isinstance(result, list)
        assert len(result) == 2

    @patch("astock_signals.convertible_bond.ak")
    def test_exception_returns_empty(self, mock_ak):
        mock_ak.bond_zh_cov_info.side_effect = Exception("fail")
        result = get_cb_info("123121")
        assert result == []
