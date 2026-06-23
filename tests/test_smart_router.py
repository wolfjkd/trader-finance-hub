"""
智能路由引擎测试。
"""

import pytest
import time
from unittest.mock import MagicMock

from astock_signals.smart_router import SmartRouter, SourceHealth, get_router


class TestSourceHealth:
    """SourceHealth 单元测试。"""

    def test_initial_state(self):
        h = SourceHealth(name="test")
        assert h.score == 100.0
        assert h.total_calls == 0
        assert h.is_healthy is True
        assert h.success_rate == 1.0

    def test_record_success(self):
        h = SourceHealth(name="test")
        h.record_success(100.0)
        assert h.total_calls == 1
        assert h.success_count == 1
        assert h.consecutive_fails == 0
        assert h.avg_latency_ms == 100.0

    def test_record_failure_penalizes(self):
        h = SourceHealth(name="test")
        h.record_failure()
        assert h.score < 100.0
        assert h.consecutive_fails == 1
        assert h.fail_count == 1

    def test_consecutive_failures_kill_score(self):
        h = SourceHealth(name="test")
        for _ in range(5):
            h.record_failure()
        assert h.score == 0.0
        assert h.is_healthy is False

    def test_success_resets_consecutive(self):
        h = SourceHealth(name="test")
        h.record_failure()
        h.record_failure()
        h.record_success(50.0)
        assert h.consecutive_fails == 0

    def test_high_latency_penalty(self):
        h = SourceHealth(name="test")
        h.record_success(15000.0)  # 15秒延迟
        assert h.score < 100.0

    def test_recover(self):
        h = SourceHealth(name="test")
        h.score = 60.0
        h.recover(20.0)
        assert h.score == 80.0

    def test_recover_capped_at_100(self):
        h = SourceHealth(name="test")
        h.score = 95.0
        h.recover(20.0)
        assert h.score == 100.0


class TestSmartRouter:
    """SmartRouter 单元测试。"""

    def test_register_and_route_success(self):
        router = SmartRouter()
        mock_fn = MagicMock(return_value={"price": 1800})
        router.register("quote", "source_a", mock_fn, priority=1)
        result, source = router.route("quote", code="600519")
        assert result == {"price": 1800}
        assert source == "source_a"
        mock_fn.assert_called_once_with(code="600519")

    def test_fallback_on_failure(self):
        router = SmartRouter()
        fail_fn = MagicMock(side_effect=Exception("network error"))
        ok_fn = MagicMock(return_value={"price": 1800})
        router.register("quote", "bad_source", fail_fn, priority=1)
        router.register("quote", "good_source", ok_fn, priority=2)
        result, source = router.route("quote")
        assert source == "good_source"
        ok_fn.assert_called_once()

    def test_all_fail_raises(self):
        router = SmartRouter()
        fail_fn = MagicMock(side_effect=Exception("fail"))
        router.register("quote", "src1", fail_fn, priority=1)
        router.register("quote", "src2", fail_fn, priority=2)
        with pytest.raises(RuntimeError, match="All sources"):
            router.route("quote")

    def test_no_sources_raises(self):
        router = SmartRouter()
        with pytest.raises(RuntimeError, match="No data source"):
            router.route("nonexistent")

    def test_health_report(self):
        router = SmartRouter()
        fn = MagicMock(return_value="ok")
        router.register("quote", "src1", fn)
        router.route("quote")
        report = router.get_health_report()
        assert len(report) == 1
        assert report[0]["source"] == "quote:src1"
        assert report[0]["total_calls"] == 1

    def test_healthy_source_preferred(self):
        """健康的源应该优先于不健康的源。"""
        router = SmartRouter()
        good_fn = MagicMock(return_value="good")
        bad_fn = MagicMock(side_effect=Exception("bad"))

        # 先让 bad_source 多次失败
        router.register("quote", "bad_source", bad_fn, priority=1)
        router.register("quote", "good_source", good_fn, priority=2)

        # 让 bad_source 失败 5 次
        for _ in range(5):
            try:
                router.route("quote")
            except RuntimeError:
                pass

        # 现在 good_source 应该是唯一健康的
        result, source = router.route("quote")
        assert source == "good_source"
