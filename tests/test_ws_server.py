"""
WebSocket 服务器测试。
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from astock_signals.ws_server import WsServer


class TestWsServer:
    """WsServer 单元测试。"""

    def test_initial_state(self):
        server = WsServer()
        assert server.is_running is False
        assert server.client_count == 0

    def test_configurable_host_port(self):
        server = WsServer(host="127.0.0.1", port=9999)
        assert server.host == "127.0.0.1"
        assert server.port == 9999

    @pytest.mark.asyncio
    async def test_push_quote_no_crash_when_stopped(self):
        """未启动时推送不应崩溃。"""
        server = WsServer()
        await server.push_quote("600519", {"price": 1800})
        # 不应抛异常

    @pytest.mark.asyncio
    async def test_push_signal_no_crash_when_stopped(self):
        server = WsServer()
        await server.push_signal("limit_up", {"code": "600519"})

    @pytest.mark.asyncio
    async def test_push_tick_no_crash_when_stopped(self):
        server = WsServer()
        await server.push_tick("600519", {"price": 1800, "volume": 100})
