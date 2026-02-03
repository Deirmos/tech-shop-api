import json
import logging

import aio_pika
from pydantic import ValidationError

from backend.core.config import settings
from backend.core.rabbitmq import setup_rabbitmq
from backend.schemas.email_event import EmailOrderConfirmationEvent
from backend.services.email_service import email_service

logger = logging.getLogger(__name__)


def _get_retry_count(message: aio_pika.IncomingMessage) -> int:
    headers = message.headers or {}
    x_death = headers.get("x-death", [])
    count = 0
    for item in x_death:
        try:
            if item.get("queue") == settings.RABBITMQ_EMAIL_QUEUE:
                count += int(item.get("count", 0))
        except Exception:
            continue
    return count

async def main():
    await setup_rabbitmq()

    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    dlq_exchange = await channel.get_exchange(settings.RABBITMQ_DLQ_EXCHANGE)

    queue = await channel.declare_queue(
        settings.RABBITMQ_EMAIL_QUEUE,
        durable=True,
        arguments={
            "x-dead-letter-exchange": settings.RABBITMQ_RETRY_EXCHANGE,
            "x-dead-letter-routing-key": settings.RABBITMQ_RETRY_QUEUE,
        },
    )

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            try:
                payload = json.loads(message.body)
                event = EmailOrderConfirmationEvent(**payload)
            except (json.JSONDecodeError, ValidationError) as exc:
                logger.warning("Invalid email event payload. Sending to DLQ.", exc_info=True)
                await dlq_exchange.publish(
                    aio_pika.Message(
                        body=message.body,
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                        content_type="application/json",
                        headers={"error": str(exc)},
                    ),
                    routing_key=settings.RABBITMQ_DLQ_QUEUE,
                )
                await message.ack()
                continue

            retry_count = _get_retry_count(message)
            if retry_count >= settings.RABBITMQ_MAX_RETRIES:
                logger.error("Email event exceeded max retries. Sending to DLQ.")
                await dlq_exchange.publish(
                    aio_pika.Message(
                        body=message.body,
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                        content_type="application/json",
                        headers={"error": "max_retries_exceeded"},
                    ),
                    routing_key=settings.RABBITMQ_DLQ_QUEUE,
                )
                await message.ack()
                continue

            try:
                await email_service.send_order_confirmation(
                    email_to=event.email_to,
                    template_data=event.template_data
                )
                await message.ack()
            except Exception:
                logger.warning("Email send failed; retrying via DLQ/TTL.", exc_info=True)
                await message.nack(requeue=False)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
