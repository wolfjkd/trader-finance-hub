"""
Tick 存储引擎测试。
"""

import pytest
import pandas as pd

from astock_signals.tick_store import TickStore


class TestTickStore:
    """TickStore 单元测试（使用临时数据库）。"""

    def test_save_and_load(self, tmp_tick_db, sample_tick_data):
        store = TickStore(db_path=tmp_tick_db)
        inserted = store.save_tick("600519", "20260624", sample_tick_data)
        assert inserted > 0

        df = store.load_tick("600519", "20260624")
        assert not df.empty
        assert len(df) == 3
        assert "time" in df.columns
        assert "price" in df.columns

    def test_dedup_on_save(self, tmp_tick_db, sample_tick_data):
        store = TickStore(db_path=tmp_tick_db)
        store.save_tick("600519", "20260624", sample_tick_data)
        store.save_tick("600519", "20260624", sample_tick_data)  # 重复
        df = store.load_tick("600519", "20260624")
        assert len(df) == 3  # 去重后仍是3条

    def test_load_nonexistent_returns_empty(self, tmp_tick_db):
        store = TickStore(db_path=tmp_tick_db)
        df = store.load_tick("999999", "20260101")
        assert df.empty

    def test_list_dates(self, tmp_tick_db, sample_tick_data):
        store = TickStore(db_path=tmp_tick_db)
        store.save_tick("600519", "20260624", sample_tick_data)
        store.save_tick("600519", "20260623", sample_tick_data)
        dates = store.list_dates("600519")
        assert len(dates) == 2
        assert "20260624" in dates

    def test_list_codes(self, tmp_tick_db, sample_tick_data):
        store = TickStore(db_path=tmp_tick_db)
        store.save_tick("600519", "20260624", sample_tick_data)
        store.save_tick("000001", "20260624", sample_tick_data)
        codes = store.list_codes()
        assert "600519" in codes
        assert "000001" in codes

    def test_get_stats(self, tmp_tick_db, sample_tick_data):
        store = TickStore(db_path=tmp_tick_db)
        store.save_tick("600519", "20260624", sample_tick_data)
        stats = store.get_stats()
        assert len(stats) == 1
        assert stats[0]["code"] == "600519"
        assert stats[0]["row_count"] == 3

    def test_save_empty_data(self, tmp_tick_db):
        store = TickStore(db_path=tmp_tick_db)
        inserted = store.save_tick("600519", "20260624", [])
        assert inserted == 0

    def test_load_with_time_filter(self, tmp_tick_db, sample_tick_data):
        store = TickStore(db_path=tmp_tick_db)
        store.save_tick("600519", "20260624", sample_tick_data)
        df = store.load_tick("600519", "20260624", start_time="09:30:02", end_time="09:30:03")
        assert len(df) == 2
