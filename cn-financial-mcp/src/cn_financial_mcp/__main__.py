"""
Entry point for running the cn-financial-mcp server.

Usage:
    python -m cn_financial_mcp                    # stdio mode (default)
    python -m cn_financial_mcp --http             # HTTP/SSE mode
    python -m cn_financial_mcp --http --port 9000 # HTTP/SSE on custom port
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="cn-financial-mcp: China Financial Data MCP Server based on AKShare"
    )
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run in HTTP/SSE mode instead of stdio",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP/SSE mode (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host for HTTP/SSE mode (default: 127.0.0.1)",
    )
    args = parser.parse_args()

    from .server import mcp

    if args.http:
        mcp._host = args.host
        mcp._port = args.port
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
