"""
ETF 数据模块测试。
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from astock_signals.etf import get_etf_realtime, get_etf_kline, get_etf_list


class TestGetEtfRealtime:
    """ETF 实时行情测试。"""

    @patch("astock_signals.etf.ak")
    def test_returns_list(self, mock_ak, sample_etf_df):
        mock_ak.fund_etf_spot_em.return_value = sample_etf_df
        result = get_etf_realtime(top_n=3)
        assert isinstance(result, list)
        assert len(result) == 3

    @patch("astock_signals.etf.ak")
    def test_has_required_fields(self, mock_ak, sample_etf_df):
        mock_ak.fund_etf_spot_em.return_value = sample_etf_df
        result = get_etf_realtime(top_n=1)
        assert "etf_code" in result[0]
        assert "name" in result[0]
        assert "price" in result[0]

    @patch("astock_signals.etf.ak")
    def test_empty_returns_empty(self, mock_ak):
        mock_ak.fund_etf_spot_em.return_value = pd.DataFrame()
        result = get_etf_realtime()
        assert result == []

    @patch("astock_signals.etf.ak")
    def test_exception_returns_empty(self, mock_ak):
        mock_ak.fund_etf_spot_em.side_effect = Exception("network error")
        result = get_etf_realtime()
        assert result == []


class TestGetEtfKline:
    """ETF K线测试。"""

    @patch("astock_signals.etf.ak")
    def test_returns_list(self, mock_ak):
        import pandas as pd
        df = pd.DataFrame({
            "日期": ["2026-06-24", "2026-06-23"],
            "开盘": [1.80, 1.79],
            "收盘": [1.85, 1.80],
            "最高": [1.86, 1.82],
            "最低": [1.79, 1.78],
            "成交量": [5000000, 4000000],
            "成交额": [9250000, 7200000],
            "涨跌幅": [2.78, 0.56],
        })
        mock_ak.fund_etf_hist_em.return_value = df
        result = get_etf_kline("513500")
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["date"] == "2026-06-24"

    @patch("astock_signals.etf.ak")
    def test_exception_returns_empty(self, mock_ak):
        mock_ak.fund_etf_hist_em.side_effect = Exception("fail")
        result = get_etf_kline("513500")
        assert result == []


class TestGetEtfList:
    """ETF 列表测试。"""

    @patch("astock_signals.etf.ak")
    def test_returns_list(self, mock_ak, sample_etf_df):
        mock_ak.fund_etf_category_sina.return_value = sample_etf_df
        result = get_etf_list()
        assert isinstance(result, list)
        assert len(result) > 0

    @patch("astock_signals.etf.ak")
    def test_exception_returns_empty(self, mock_ak):
        mock_ak.fund_etf_category_sina.side_effect = Exception("fail")
        result = get_etf_list()
        assert result == []
