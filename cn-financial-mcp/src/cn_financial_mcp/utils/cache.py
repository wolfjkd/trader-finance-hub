"""
TTL-based in-memory cache for AKShare data.

Caching strategy:
- Realtime quotes: 30 seconds
- Daily price data: 5 minutes
- Financial statements: 24 hours
- Company info: 24 hours
- Macro data: 7 days

Thread-safe with threading.Lock and configurable max_size LRU eviction.
"""

import time
import threading
from typing import Any
from collections import OrderedDict

# Default TTL values in seconds
TTL_REALTIME = 30         # Real-time quotes
TTL_DAILY = 300           # 5 minutes for daily price
TTL_FINANCIAL = 86400     # 24 hours for financial data
TTL_COMPANY = 86400       # 24 hours for company info
TTL_MACRO = 604800        # 7 days for macro data


class TTLCache:
    """Thread-safe TTL cache backed by OrderedDict with LRU eviction.

    Args:
        max_size: Maximum number of entries. Oldest entries evicted when exceeded.
                  0 means unlimited (default: 5000).
    """

    def __init__(self, max_size: int = 5000):
        self._store: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._max_size = max_size
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        """Get a cached value if it exists and hasn't expired."""
        with self._lock:
            if key in self._store:
                value, expires_at = self._store[key]
                if time.time() < expires_at:
                    # Move to end (most recently used)
                    self._store.move_to_end(key)
                    return value
                # Expired, remove it
                del self._store[key]
        return None

    def set(self, key: str, value: Any, ttl: int = TTL_DAILY) -> None:
        """Store a value with a TTL in seconds."""
        with self._lock:
            if key in self._store:
                self._store.move_to_end(key)
            self._store[key] = (value, time.time() + ttl)
            # LRU eviction
            while self._max_size > 0 and len(self._store) > self._max_size:
                self._store.popitem(last=False)

    def invalidate(self, key: str) -> None:
        """Remove a specific cached entry."""
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._store.clear()

    def cleanup(self) -> int:
        """Remove all expired entries. Returns number of entries removed."""
        now = time.time()
        with self._lock:
            expired = [k for k, (_, exp) in self._store.items() if now >= exp]
            for k in expired:
                del self._store[k]
        return len(expired)

    @property
    def size(self) -> int:
        """Number of entries in cache (including possibly expired)."""
        with self._lock:
            return len(self._store)


# Global cache instance
cache = TTLCache()
