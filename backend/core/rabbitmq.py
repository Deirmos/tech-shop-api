import asyncio
import json
import logging
from typing import Optional

import aio_pika

from backend.core.config import settings

logger = logging.getLogger(__name__)

_connection: Optional[aio_pika.RobustConnection] = None
_connection_lock = asyncio.Lock()
_topology_ready = False


async def _get_connection() -> aio_pika.RobustConnection:
    global _connection
    if _connection and not _connection.is_closed:
        return _connection
    async with _connection_lock:
        if _connection and not _connection.is_closed:
            return _connection
        _connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        return _connection


async def setup_rabbitmq() -> None:
    global _topology_ready
    if _topology_ready:
        return

    connection = await _get_connection()
    channel = await connection.channel(publisher_confirms=True)

    email_exchange = await channel.declare_exchange(
        settings.RABBITMQ_EMAIL_EXCHANGE,
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )
    retry_exchange = await channel.declare_exchange(
        settings.RABBITMQ_RETRY_EXCHANGE,
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )
    dlq_exchange = await channel.declare_exchange(
        settings.RABBITMQ_DLQ_EXCHANGE,
        aio_pika.ExchangeType.DIRECT,
        durable=True,
    )

    main_queue = await channel.declare_queue(
        settings.RABBITMQ_EMAIL_QUEUE,
        durable=True,
        arguments={
            "x-dead-letter-exchange": settings.RABBITMQ_RETRY_EXCHANGE,
            "x-dead-letter-routing-key": settings.RABBITMQ_RETRY_QUEUE,
        },
    )
    retry_queue = await channel.declare_queue(
        settings.RABBITMQ_RETRY_QUEUE,
        durable=True,
        arguments={
            "x-message-ttl": settings.RABBITMQ_RETRY_DELAY_SECONDS * 1000,
            "x-dead-letter-exchange": settings.RABBITMQ_EMAIL_EXCHANGE,
            "x-dead-letter-routing-key": settings.RABBITMQ_EMAIL_QUEUE,
        },
    )
    dlq_queue = await channel.declare_queue(
        settings.RABBITMQ_DLQ_QUEUE,
        durable=True,
    )

    await main_queue.bind(email_exchange, routing_key=settings.RABBITMQ_EMAIL_QUEUE)
    await retry_queue.bind(retry_exchange, routing_key=settings.RABBITMQ_RETRY_QUEUE)
    await dlq_queue.bind(dlq_exchange, routing_key=settings.RABBITMQ_DLQ_QUEUE)

    _topology_ready = True


async def publisher_email_event(payload: dict) -> None:
    await setup_rabbitmq()

    connection = await _get_connection()
    channel = await connection.channel(publisher_confirms=True)
    email_exchange = await channel.get_exchange(settings.RABBITMQ_EMAIL_EXCHANGE)

    message = aio_pika.Message(
        body=json.dumps(payload).encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        content_type="application/json",
    )

    last_error: Optional[Exception] = None
    for attempt in range(1, settings.RABBITMQ_MAX_RETRIES + 1):
        try:
            await email_exchange.publish(
                message, routing_key=settings.RABBITMQ_EMAIL_QUEUE
            )
            return
        except Exception as exc:  # pragma: no cover - depends on broker state
            last_error = exc
            delay = min(2 ** attempt, 10)
            logger.warning(
                "RabbitMQ publish failed (attempt %s/%s). Retrying in %ss.",
                attempt,
                settings.RABBITMQ_MAX_RETRIES,
                delay,
                exc_info=True,
            )
            await asyncio.sleep(delay)

    logger.error("RabbitMQ publish failed after retries.", exc_info=last_error)
    if last_error:
        raise last_error
