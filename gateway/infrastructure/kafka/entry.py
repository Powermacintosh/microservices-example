import asyncio
from fastapi import FastAPI
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from infrastructure.kafka.producer import producer

STARTUP_RETRIES = 3
RETRY_BACKOFF = 1.0

async def _start_producer_with_retries():
    last_exc = None
    for i in range(1, STARTUP_RETRIES + 1):
        try:
            await producer.start()
            return
        except Exception as exc:
            last_exc = exc
            await asyncio.sleep(RETRY_BACKOFF * i)
    raise last_exc

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup
    await _start_producer_with_retries()
    app.state.kafka_producer_available = True
    try:
        yield
    finally:
        # shutdown
        try:
            await producer.stop()
        except Exception:
            pass