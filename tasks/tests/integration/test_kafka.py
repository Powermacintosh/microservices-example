import pytest, asyncio, httpx, json
from fastapi import status
from httpx import AsyncClient
from aiokafka import AIOKafkaConsumer
from core.config import settings


class TestTaskKafkaIntegration:
    """
    Тесты для интеграции менеджера задач с использованием Kafka.
    """
    async def wait_for_server(self, url: str, timeout: int = 30) -> bool:
        """
        Ожидает подключения к серверу.
        """
        base_url=f'http://tasks_app_test:{settings.api_v1_port}'
        start_time = asyncio.get_event_loop().time()
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    await client.get(base_url + url)
                return True
            except httpx.ConnectError:
                if asyncio.get_event_loop().time() - start_time > timeout:
                    raise TimeoutError('Не удалось подключиться к серверу за отведенное время.')
                await asyncio.sleep(1)
    
    @pytest.mark.asyncio
    async def test_create_task_event(
        self, httpx_client: AsyncClient,
        kafka_consumer: AIOKafkaConsumer
    ):
        """
        Тест корректного создания задачи через Kafka.
        """
        url = '/api/v1/task/create_event'
        await self.wait_for_server(url)
        response_task = await httpx_client.post(
            url, 
            json={
                'title': 'Create Task', 
                'description': None,
            }
        )
        data_response_task = response_task.json()
        assert response_task.status_code == status.HTTP_201_CREATED
        assert data_response_task['status'] == 'published'

        # Пробуем поймать
        received = None
        for _ in range(25):
            try:
                msg = await asyncio.wait_for(kafka_consumer.getone(), timeout=2)
                if msg:
                    received = json.loads(msg.value.decode('utf-8'))
                    break
            except Exception:
                await asyncio.sleep(1)

        assert received is not None
        assert received['event'] == 'TaskModuleCreation'
        assert received['task']['title'] == 'Create Task'
