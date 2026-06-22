"""
Anti-ban rate-limited HTTP client for Eastmoney APIs.

东财系 HTTP 接口（push2 / push2his / datacenter-web / search-api / np-weblist）
有风控：每秒 >5 次 / 单 IP 并发 ≥10 / 1 分钟 ≥200 次 / 5 分钟 ≥300 次 → 临时封 IP。

所有 eastmoney.com 请求一律走此入口：串行限流（最小间隔 + 随机抖动）+ 复用 Keep-Alive 会话。

TradingAgents-astock 移植模块。V0.1。
"""

from __future__ import annotations

import os
import random
import time
import logging

import requests as _requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_EM_SESSION: _requests.Session | None = None
_EM_MIN_INTERVAL: float = float(os.environ.get("EM_MIN_INTERVAL", "1.0"))
_em_last_call: list[float] = [0.0]  # mutable for inner func access

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

_DATACENTER_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"


def _ensure_session() -> _requests.Session:
    """Get or create the shared Eastmoney session (lazy init)."""
    global _EM_SESSION
    if _EM_SESSION is None:
        _EM_SESSION = _requests.Session()
        _EM_SESSION.headers.update({"User-Agent": _UA})
    return _EM_SESSION


# ---------------------------------------------------------------------------
# Public API: rate-limited request
# ---------------------------------------------------------------------------


def em_get(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: int = 15,
    **kwargs,
) -> _requests.Response:
    """东财统一请求入口：自动节流 + 复用 session + 默认 UA。

    所有 eastmoney.com 接口都应通过它请求，避免多 Agent 高频拉数据被封 IP。
    串行限流：与上次东财请求间隔 < EM_MIN_INTERVAL 时 sleep 补足 + 0.1~0.5s 随机抖动。

    Args:
        url: Full URL to request.
        params: Query parameters dict.
        headers: Optional per-request headers (e.g. Referer/Origin).
        timeout: Request timeout in seconds.
        **kwargs: Passed to session.get().

    Returns:
        requests.Response object.
    """
    wait = _EM_MIN_INTERVAL - (time.time() - _em_last_call[0])
    if wait > 0:
        time.sleep(wait + random.uniform(0.1, 0.5))
    try:
        return _ensure_session().get(
            url, params=params, headers=headers, timeout=timeout, **kwargs
        )
    finally:
        _em_last_call[0] = time.time()


def set_min_interval(seconds: float) -> None:
    """Adjust the minimum interval between Eastmoney requests.

    Args:
        seconds: Minimum seconds between requests (default 1.0).
    """
    global _EM_MIN_INTERVAL
    _EM_MIN_INTERVAL = float(seconds)


def em_reset_session() -> None:
    """Close and recreate the Eastmoney session (e.g. after IP change)."""
    global _EM_SESSION
    if _EM_SESSION is not None:
        try:
            _EM_SESSION.close()
        except Exception:
            pass
        _EM_SESSION = None


# ---------------------------------------------------------------------------
# Eastmoney Datacenter unified query helper
# ---------------------------------------------------------------------------


def em_datacenter(
    report_name: str,
    columns: str = "ALL",
    filter_str: str = "",
    page_size: int = 50,
    sort_columns: str = "",
    sort_types: str = "-1",
) -> list[dict]:
    """东财数据中心统一查询 — 龙虎榜/解禁 等共用入口。

    Args:
        report_name: Report name, e.g. "RPT_LIFT_STAGE", "RPT_DAILYBILLBOARD_DETAILSNEW".
        columns: Column selection, "ALL" for everything.
        filter_str: Filter expression, e.g. '(SECURITY_CODE="000858")'.
        page_size: Results per page (max 200).
        sort_columns: Column name to sort by.
        sort_types: Sort direction (-1=desc, 1=asc).

    Returns:
        List of dicts, each representing one row.
    """
    params = {
        "reportName": report_name,
        "columns": columns,
        "filter": filter_str,
        "pageNumber": "1",
        "pageSize": str(page_size),
        "sortColumns": sort_columns,
        "sortTypes": sort_types,
        "source": "WEB",
        "client": "WEB",
    }
    r = em_get(_DATACENTER_URL, params=params, timeout=15)
    d = r.json()
    if d.get("result") and d["result"].get("data"):
        return d["result"]["data"]
    return []


# ---------------------------------------------------------------------------
# Convenience: push2 / push2his direct request helpers
# ---------------------------------------------------------------------------


def em_push2(params: dict, timeout: int = 15) -> dict:
    """Query Eastmoney push2 API (realtime market data).

    Args:
        params: Query parameters dict.
        timeout: Request timeout.

    Returns:
        Parsed JSON dict.
    """
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    r = em_get(url, params=params, timeout=timeout)
    return r.json()


def em_push2_fund_flow(secid: str, timeout: int = 10) -> dict:
    """Query Eastmoney push2 fund flow API (minute-level).

    Args:
        secid: Security ID, e.g. "1.600519" or "0.000858".
        timeout: Request timeout.

    Returns:
        Parsed JSON dict with klines data.
    """
    url = "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"
    params = {
        "secid": secid,
        "klt": 1,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57",
    }
    r = em_get(url, params=params, timeout=timeout)
    return r.json()


def em_push2his_fund_flow(secid: str, limit: int = 20, timeout: int = 10) -> dict:
    """Query Eastmoney push2his fund flow API (daily historical).

    Args:
        secid: Security ID.
        limit: Number of trading days.
        timeout: Request timeout.

    Returns:
        Parsed JSON dict with daily klines.
    """
    url = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
    params = {
        "secid": secid,
        "lmt": limit,
        "klt": 101,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57",
    }
    r = em_get(url, params=params, timeout=timeout)
    return r.json()
