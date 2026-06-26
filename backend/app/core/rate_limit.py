"""Redis-backed fixed-window rate limiter exposed as a FastAPI dependency.

Usage:
    @router.post("/login", dependencies=[Depends(RateLimiter(times=5, seconds=60))])

If Redis is unavailable, requests are allowed (fail-open) so the app stays
usable in environments without Redis (e.g. some test runs). Tests that assert
limiting use a real/fake Redis.
"""
from typing import Optional

import redis.asyncio as aioredis
from fastapi import Depends, Request

from app.core.config import settings
from app.core.exceptions import RateLimitError
from app.core.logging_config import get_logger

logger = get_logger("rate_limit")

_redis: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


def _client_key(request: Request, scope: str) -> str:
    # Prefer authenticated user id if present, else client host.
    user_id = getattr(request.state, "user_id", None)
    ident = user_id or (request.client.host if request.client else "anon")
    return f"ratelimit:{scope}:{ident}"


class RateLimiter:
    def __init__(self, times: int, seconds: int, scope: Optional[str] = None):
        self.times = times
        self.seconds = seconds
        self.scope = scope

    async def __call__(
        self, request: Request, redis: aioredis.Redis = Depends(get_redis)
    ) -> None:
        scope = self.scope or request.url.path
        key = _client_key(request, scope)
        try:
            current = await redis.incr(key)
            if current == 1:
                await redis.expire(key, self.seconds)
        except Exception as exc:  # fail-open
            logger.warning("rate limiter unavailable: %s", exc)
            return
        if current > self.times:
            raise RateLimitError(
                f"Rate limit exceeded: {self.times} requests per {self.seconds}s"
            )
