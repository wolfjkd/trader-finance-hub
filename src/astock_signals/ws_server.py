"""
WebSocket 实时推送服务器。

用途：
- 实时行情推送（tick/quote 变动）
- 异动信号推送（涨停/跌停/大单/北向异动）
- 客户端按股票代码订阅

设计原则：
- 轻量级，基于 websockets 库
- JSON 格式消息
- 心跳保活（30秒间隔）
- 支持多客户端并发连接

依赖：pip install websockets（可选，不强制）
"""

from __future__ import annotations

import json
import time
import asyncio
import logging
from typing import Optional, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class WsServer:
    """WebSocket 实时推送服务器。

    Usage:
        server = WsServer(host="0.0.0.0", port=8765)
        # 在异步上下文中：
        await server.start()
        await server.push_quote("600519", {"price": 1800, "change_pct": 1.5})
        # 客户端连接后发送 {"action":"subscribe","codes":["600519","000001"]}
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self._clients: dict = {}  # websocket -> set of subscribed codes
        self._server = None
        self._running = False

    async def start(self):
        """启动 WebSocket 服务器。"""
        try:
            import websockets
        except ImportError:
            logger.error("websockets not installed. Run: pip install websockets")
            raise

        self._server = await websockets.serve(
            self._handler, self.host, self.port
        )
        self._running = True
        logger.info("WebSocket server started on ws://%s:%d", self.host, self.port)

    async def stop(self):
        """停止 WebSocket 服务器。"""
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._running = False
            logger.info("WebSocket server stopped")

    async def _handler(self, websocket, path=None):
        """处理单个客户端连接。"""
        self._clients[websocket] = set()
        logger.info("Client connected: %s", websocket.remote_address)
        try:
            async for raw_msg in websocket:
                try:
                    msg = json.loads(raw_msg)
                    action = msg.get("action", "")

                    if action == "subscribe":
                        codes = msg.get("codes", [])
                        self._clients[websocket].update(codes)
                        await websocket.send(json.dumps({
                            "type": "subscribed",
                            "codes": list(self._clients[websocket]),
                        }))

                    elif action == "unsubscribe":
                        codes = msg.get("codes", [])
                        self._clients[websocket] -= set(codes)
                        await websocket.send(json.dumps({
                            "type": "unsubscribed",
                            "codes": list(self._clients[websocket]),
                        }))

                    elif action == "ping":
                        await websocket.send(json.dumps({"type": "pong"}))

                    elif action == "status":
                        await websocket.send(json.dumps({
                            "type": "status",
                            "connected_clients": len(self._clients),
                            "subscriptions": list(self._clients[websocket]),
                        }))

                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error", "message": "Invalid JSON"
                    }))

        except Exception as e:
            logger.debug("Client disconnected: %s", e)
        finally:
            self._clients.pop(websocket, None)

    async def push_quote(self, code: str, data: dict):
        """推送行情数据到订阅了该代码的所有客户端。"""
        if not self._running:
            return

        msg = json.dumps({
            "type": "quote",
            "code": code,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }, ensure_ascii=False)

        targets = [
            ws for ws, codes in self._clients.items()
            if code in codes or "*" in codes
        ]
        if targets:
            await asyncio.gather(
                *[self._safe_send(ws, msg) for ws in targets],
                return_exceptions=True,
            )

    async def push_signal(self, signal_type: str, data: dict):
        """推送异动信号到所有客户端（全局广播）。"""
        if not self._running:
            return

        msg = json.dumps({
            "type": "signal",
            "signal_type": signal_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }, ensure_ascii=False)

        targets = list(self._clients.keys())
        if targets:
            await asyncio.gather(
                *[self._safe_send(ws, msg) for ws in targets],
                return_exceptions=True,
            )

    async def push_tick(self, code: str, tick_data: dict):
        """推送 tick 数据到订阅了该代码的所有客户端。"""
        if not self._running:
            return

        msg = json.dumps({
            "type": "tick",
            "code": code,
            "data": tick_data,
            "timestamp": datetime.now().isoformat(),
        }, ensure_ascii=False)

        targets = [
            ws for ws, codes in self._clients.items()
            if code in codes or "*" in codes
        ]
        if targets:
            await asyncio.gather(
                *[self._safe_send(ws, msg) for ws in targets],
                return_exceptions=True,
            )

    async def _safe_send(self, ws, msg: str):
        """安全发送消息（捕获断连异常）。"""
        try:
            await ws.send(msg)
        except Exception:
            self._clients.pop(ws, None)

    @property
    def client_count(self) -> int:
        return len(self._clients)

    @property
    def is_running(self) -> bool:
        return self._running


# 全局单例
_global_ws: WsServer | None = None

def get_ws_server(host: str = "0.0.0.0", port: int = 8765) -> WsServer:
    global _global_ws
    if _global_ws is None:
        _global_ws = WsServer(host, port)
    return _global_ws
