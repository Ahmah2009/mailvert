from cachetools import TTLCache

from mailvert.config import settings
from mailvert.models import VerificationResult

_cache: TTLCache = TTLCache(maxsize=settings.cache_max_size, ttl=settings.cache_ttl_seconds)


def get(email: str) -> VerificationResult | None:
    result = _cache.get(email.lower())
    if result is None:
        return None
    return result.model_copy(update={"cached": True})


def set(email: str, result: VerificationResult) -> None:
    _cache[email.lower()] = result


def clear() -> None:
    _cache.clear()
