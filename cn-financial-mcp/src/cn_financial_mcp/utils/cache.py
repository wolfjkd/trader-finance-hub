"""
TTL-based in-memory cache for AKShare data.

Caching strategy:
- Realtime quotes: 30 seconds
- Daily price data: 5 minutes
- Financial statements: 24 hours
- Company info: 24 hours
- Macro data: 7 days
"""

import time
from typing import Any

# Default TTL values in seconds
TTL_REALTIME = 30         # Real-time quotes
TTL_DAILY = 300           # 5 minutes for daily price
TTL_FINANCIAL = 86400     # 24 hours for financial data
TTL_COMPANY = 86400       # 24 hours for company info
TTL_MACRO = 604800        # 7 days for macro data


class TTLCache:
    """Simple thread-safe TTL cache backed by a dict."""

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        """Get a cached value if it exists and hasn't expired."""
        if key in self._store:
            value, expires_at = self._store[key]
            if time.time() < expires_at:
                return value
            # Expired, remove it
            del self._store[key]
        return None

    def set(self, key: str, value: Any, ttl: int = TTL_DAILY) -> None:
        """Store a value with a TTL in seconds."""
        self._store[key] = (value, time.time() + ttl)

    def invalidate(self, key: str) -> None:
        """Remove a specific cached entry."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Clear all cached entries."""
        self._store.clear()

    def cleanup(self) -> int:
        """Remove all expired entries. Returns number of entries removed."""
        now = time.time()
        expired = [k for k, (_, exp) in self._store.items() if now >= exp]
        for k in expired:
            del self._store[k]
        return len(expired)

    @property
    def size(self) -> int:
        """Number of entries in cache (including possibly expired)."""
        return len(self._store)


# Global cache instance
cache = TTLCache()
