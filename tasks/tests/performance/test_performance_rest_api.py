import pytest, asyncio, httpx, time, sys
from core.config import settings
from fastapi import status


class TestPerformanceTaskRestAPI:
    """
    Тесты производительности для REST API менеджера задач.
    """
    @pytest.mark.skipif(sys.platform == 'linux', reason='Тест работает только на Linux')
    def test_only_on_linux(self):
        # Тест, который работает только на Linux.
        assert True

    def setup_method(self):
        # Инициализация атрибута перед каждым тестом класса
        self.value = 55

    @classmethod
    def setup_class(cls):
        # Инициализация атрибута перед всеми тестами класса
        cls.base_url=f'http://tasks_app_test:{settings.api_v1_port}'

    async def wait_for_server(self, url: str, timeout: int = 30) -> bool:
        """
        Ожидает подключения к серверу.
        """
        start_time = asyncio.get_event_loop().time()
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    await client.get(self.base_url + url)
                return True
            except httpx.ConnectError:
                if asyncio.get_event_loop().time() - start_time > timeout:
                    raise TimeoutError('Не удалось подключиться к серверу за отведенное время.')
                await asyncio.sleep(1)
    
    @pytest.mark.asyncio
    async def test_load(self):
        await self.wait_for_server('/api/v1/task/1/')
        async def make_request():
            async with httpx.AsyncClient() as client:
                response = await client.get(f'{self.base_url}/api/v1/task/1/')
                return response

        tasks = [make_request() for _ in range(100)]
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        # Проверка успешности запросов
        for response in responses:
            assert response.status_code == status.HTTP_404_NOT_FOUND

        print(f'Время выполнения запросов: {end_time - start_time:.2f} секунд')