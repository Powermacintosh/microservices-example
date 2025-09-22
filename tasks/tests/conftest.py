import pytest, asyncio, uuid
from typing import AsyncIterator
from aiokafka import AIOKafkaConsumer
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from main import app
from core.config import settings


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    if settings.MODE != 'TEST':
        for item in items:
            item.add_marker(pytest.mark.skip(reason=f'В режиме {settings.MODE}, тесты недоступны!'))

class TestingUnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self) -> None:
        await self.session.commit()
        
    async def rollback(self) -> None:
        await self.session.rollback()

    async def close(self) -> None:
        await self.session.close()

@pytest.fixture(scope='function')
async def testing_db_connection() -> AsyncIterator[TestingUnitOfWork]:
    """Фикстура для работы с Unit of Work в тестах"""
    engine = create_async_engine(
        url=settings.db.async_url,
        echo=settings.db.echo,
    )
    testing_async_session = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    async with testing_async_session() as session:
        uow = TestingUnitOfWork(session)
        try:
            yield uow
            await uow.commit()
        except Exception:
            await uow.rollback()
            raise
        finally:
            await uow.close()

# Фикстура для HTTPX клиента
@pytest.fixture(scope='function')
async def httpx_client():
    async with AsyncClient(base_url=f'http://tasks_app_test:{settings.api_v1_port}') as async_client:
        yield async_client

@pytest.fixture(scope='function')
async def kafka_consumer() -> AIOKafkaConsumer:
    """Фикстура Kafka Consumer."""
    consumer = AIOKafkaConsumer(
        settings.kafka.TOPIC,
        bootstrap_servers=settings.kafka.BOOTSTRAP,
        group_id=f'test-group-{uuid.uuid4()}',
        enable_auto_commit=False,
        auto_offset_reset='earliest',
    )
    await consumer.start()
    try:
        await asyncio.sleep(1)
        await consumer.seek_to_beginning()
        yield consumer
    finally:
        await consumer.stop()


