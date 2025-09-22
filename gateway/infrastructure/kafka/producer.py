import asyncio, json
from fastapi import FastAPI
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from aiokafka import AIOKafkaProducer
from core.config import settings


async def _start_producer_with_retries(producer: AIOKafkaProducer):
    last_exc = None
    for i in range(1, settings.kafka.STARTUP_RETRIES + 1):
        try:
            await producer.start()
            return
        except Exception as exc:
            last_exc = exc
            await asyncio.sleep(settings.kafka.RETRY_BACKOFF * i)
    raise last_exc

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka.BOOTSTRAP,
        client_id=settings.kafka.CLIENT_ID,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    )
    # startup
    await _start_producer_with_retries(producer)
    app.state.kafka_producer = producer
    app.state.kafka_producer_available = True
    try:
        yield
    finally:
        # shutdown
        try:
            await producer.stop()
        except Exception:
            pass