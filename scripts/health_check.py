#!/usr/bin/env python3
"""
金融数据中枢 - 数据源健康检测脚本
检测所有 MCP 数据源的可用性和响应速度
"""

import subprocess
import json
import time
import sys
from datetime import datetime

# 数据源定义
DATA_SOURCES = {
    "tencent": {
        "name": "腾讯接口",
        "type": "HTTP",
        "test_url": "https://qt.gtimg.cn/q=sh000001",
        "priority": "P0"
    },
    "tdx": {
        "name": "通达信 MCP",
        "type": "MCP",
        "test_command": "tdx-connector auto-detect",
        "priority": "P0"
    },
    "wind": {
        "name": "Wind MCP",
        "type": "MCP+CLI",
        "test_command": "node ~/.workbuddy/skills/wind-mcp-skill/scripts/cli.mjs health",
        "priority": "P1"
    },
    "eastmoney": {
        "name": "东方财富 MCP",
        "type": "MCP",
        "test_command": "python -c \"from cn_financial_mcp.server import mcp; print('OK')\"",
        "priority": "P1"
    },
    "ftshare": {
        "name": "ftshare 公告",
        "type": "CLI",
        "test_command": "python ~/.workbuddy/skills/ftshare-announcement-data/run.py stock-announcements-single-stock-all-periods --stock-code 600170.SH --page 1 --page-size 1",
        "priority": "P2"
    }
}


def test_http(url: str) -> dict:
    """测试 HTTP 接口"""
    try:
        import urllib.request
        start = time.time()
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode("gbk", errors="ignore")
            elapsed = (time.time() - start) * 1000
            return {
                "status": "OK",
                "latency_ms": round(elapsed, 1),
                "data_size": len(data)
            }
    except Exception as e:
        return {
            "status": "FAIL",
            "error": str(e)[:100]
        }


def test_command(cmd: str) -> dict:
    """测试命令行工具"""
    try:
        start = time.time()
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=30
        )
        elapsed = (time.time() - start) * 1000
        ok = result.returncode == 0 and len(result.stdout.strip()) > 0
        return {
            "status": "OK" if ok else "FAIL",
            "latency_ms": round(elapsed, 1),
            "exit_code": result.returncode,
            "output_len": len(result.stdout)
        }
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "error": "30s timeout"}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)[:100]}


def main():
    print(f"=== 数据源健康检测 ===")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = {}
    for key, src in DATA_SOURCES.items():
        print(f"检测 {src['name']} ({src['type']})...", end=" ", flush=True)

        if src["type"] == "HTTP":
            result = test_http(src["test_url"])
        else:
            result = test_command(src["test_command"])

        results[key] = {**src, **result}

        icon = "OK" if result.get("status") == "OK" else "FAIL"
        latency = result.get("latency_ms", "N/A")
        print(f"[{icon}] {latency}ms")

    # 汇总
    print(f"\n=== 检测汇总 ===")
    ok_count = sum(1 for r in results.values() if r.get("status") == "OK")
    total = len(results)
    print(f"可用: {ok_count}/{total}")

    for key, r in results.items():
        status_icon = "+" if r.get("status") == "OK" else "-"
        latency = f"{r.get('latency_ms', 'N/A')}ms"
        print(f"  [{status_icon}] {r['name']:12s} {r['priority']:4s} {latency:>10s}")

    return 0 if ok_count >= total * 0.6 else 1


if __name__ == "__main__":
    sys.exit(main())
