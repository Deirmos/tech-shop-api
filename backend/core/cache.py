import functools
import inspect
import json
import logging
from decimal import Decimal
from typing import Iterable

from fastapi.encoders import jsonable_encoder
from redis import asyncio as redis

from backend.core.config import settings

logger = logging.getLogger(__name__)

_redis: redis.Redis | None = None


def get_redis() -> redis.Redis | None:
    url = getattr(settings, "REDIS_URL", None)
    if not url:
        return None

    global _redis
    if _redis is None:
        _redis = redis.from_url(url, encoding="utf-8", decode_responses=True)
    return _redis


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return ""


def _normalize(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, str):
        return value.strip().lower()
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (list, tuple, set)):
        return json.dumps([_normalize(v) for v in value], ensure_ascii=False)
    if isinstance(value, dict):
        return json.dumps({k: _normalize(v) for k, v in value.items()}, ensure_ascii=False, sort_keys=True)
    return str(value)


def _build_cache_key(template: str, fn, args, kwargs, exclude: Iterable[str]) -> str:
    bound = inspect.signature(fn).bind_partial(*args, **kwargs)
    bound.apply_defaults()
    data = {
        k: _normalize(v)
        for k, v in bound.arguments.items()
        if k not in exclude
    }
    return f"api_cache:{template.format_map(_SafeDict(data))}"


def _decode_cached(decoder, data):
    if decoder is None:
        return data
    if isinstance(data, list):
        return [decoder.model_validate(item) if hasattr(decoder, "model_validate") else decoder(item) for item in data]
    return decoder.model_validate(data) if hasattr(decoder, "model_validate") else decoder(data)


def cacheable(
    ttl: int,
    key: str,
    exclude: Iterable[str] | None = None,
    decoder=None,
):
    exclude_set = set(exclude or [])
    exclude_set.update({"db", "current_user", "current_admin", "admin", "user", "background_tasks"})

    def decorator(fn):
        sig = inspect.signature(fn)

        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            redis_client = get_redis()
            if redis_client is None:
                return await fn(*args, **kwargs)

            cache_key = _build_cache_key(key, fn, args, kwargs, exclude_set)

            try:
                cached = await redis_client.get(cache_key)
                if cached is not None:
                    return _decode_cached(decoder, json.loads(cached))
            except Exception:
                logger.debug("Cache read failed for key %s", cache_key, exc_info=True)

            result = await fn(*args, **kwargs)
            if decoder is not None:
                result = _decode_cached(decoder, jsonable_encoder(result))

            try:
                payload = json.dumps(
                    jsonable_encoder(result),
                    ensure_ascii=False,
                    default=str,
                )
                await redis_client.set(cache_key, payload, ex=ttl)
            except Exception:
                logger.debug("Cache write failed for key %s", cache_key, exc_info=True)

            return result

        wrapper.__signature__ = sig
        return wrapper

    return decorator


async def _delete_pattern(redis_client: redis.Redis, pattern: str) -> None:
    cursor = 0
    while True:
        cursor, keys = await redis_client.scan(cursor=cursor, match=pattern, count=200)
        if keys:
            await redis_client.delete(*keys)
        if cursor == 0:
            break


def cache_invalidate(patterns: Iterable[str]):
    patterns_list = list(patterns)

    def decorator(fn):
        sig = inspect.signature(fn)

        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            result = await fn(*args, **kwargs)

            redis_client = get_redis()
            if redis_client is None:
                return result

            for pattern in patterns_list:
                full_pattern = f"api_cache:{pattern}"
                try:
                    await _delete_pattern(redis_client, full_pattern)
                except Exception:
                    logger.debug("Cache invalidation failed for pattern %s", full_pattern, exc_info=True)

            return result

        wrapper.__signature__ = sig
        return wrapper

    return decorator
