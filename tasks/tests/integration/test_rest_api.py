import pytest, asyncio, httpx
from fastapi import status
from httpx import AsyncClient
from core.config import settings


class TestTaskRestAPI:
    """
    Тесты для REST API менеджера задач с использованием httpx.
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
    
    @pytest.fixture
    async def test_create_task(self, httpx_client: AsyncClient):
        """
        Тест корректного создания задачи.
        """
        url = '/api/v1/task/create'
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
        assert data_response_task['title'] == 'Create Task'
        assert data_response_task['description'] == None
        assert data_response_task['status'] == 'created'
        return data_response_task
    
    @pytest.mark.asyncio
    async def test_get_current_task(self, httpx_client: AsyncClient, test_create_task: dict):
        url = f'/api/v1/task/{test_create_task["id"]}/'
        await self.wait_for_server(url)
        assert test_create_task is not None
        response = await httpx_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        data_response_task = response.json()
        assert data_response_task['id'] == test_create_task['id']
        assert data_response_task['title'] == test_create_task['title']
        assert data_response_task['description'] == test_create_task['description']
        assert data_response_task['status'] == test_create_task['status']
    
    @pytest.mark.asyncio
    async def test_get_failed_task(self, httpx_client: AsyncClient, test_create_task: dict):
        url = '/api/v1/task/1/'
        await self.wait_for_server(url)
        assert test_create_task is not None
        response = await httpx_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data_response_task = response.json()
        assert data_response_task['detail'] == 'Задача 1 не найдена!'

    @pytest.mark.asyncio
    async def test_update_current_task(self, httpx_client: AsyncClient, test_create_task: dict):
        url = f'/api/v1/task/{test_create_task["id"]}/'
        await self.wait_for_server(url)
        assert test_create_task is not None
        response = await httpx_client.put(url, json={
            'title': 'Update Task', 
            'description': None,
            'status': 'in_progress',
        })
        assert response.status_code == status.HTTP_200_OK
        data_response_task = response.json()
        assert data_response_task['id'] == test_create_task['id']
        assert data_response_task['title'] == 'Update Task'
        assert data_response_task['description'] == None
        assert data_response_task['status'] == 'in_progress'
    
    @pytest.mark.asyncio
    async def test_update_failed_data_task(self, httpx_client: AsyncClient, test_create_task: dict):
        url = f'/api/v1/task/{test_create_task["id"]}/'
        await self.wait_for_server(url)
        assert test_create_task is not None
        response = await httpx_client.put(url, json={
            'title': 'Update Task', 
            'description': None,
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_update_failed_id_task(self, httpx_client: AsyncClient, test_create_task: dict):
        url = '/api/v1/task/1/'
        await self.wait_for_server(url)
        assert test_create_task is not None
        response = await httpx_client.put(url, json={
            'title': 'Update Task', 
            'description': None,
            'status': 'in_progress',
        })
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_update_title_current_task_partial(self, httpx_client: AsyncClient, test_create_task: dict):
        url = f'/api/v1/task/{test_create_task["id"]}/'
        await self.wait_for_server(url)
        assert test_create_task is not None
        response = await httpx_client.patch(url, json={
            'title': 'Update Task', 
        })
        assert response.status_code == status.HTTP_200_OK
        data_response_task = response.json()
        assert data_response_task['id'] == test_create_task['id']
        assert data_response_task['title'] == 'Update Task'
        assert data_response_task['description'] == test_create_task['description']
        assert data_response_task['status'] == test_create_task['status']
        
    
    @pytest.mark.asyncio
    async def test_update_description_current_task_partial(self, httpx_client: AsyncClient, test_create_task: dict):
        url = f'/api/v1/task/{test_create_task["id"]}/'
        await self.wait_for_server(url)
        assert test_create_task is not None
        response = await httpx_client.patch(url, json={
            'description': 'Description Update Task', 
        })
        assert response.status_code == status.HTTP_200_OK
        data_response_task = response.json()
        assert data_response_task['id'] == test_create_task['id']
        assert data_response_task['title'] == test_create_task['title']
        assert data_response_task['description'] == 'Description Update Task'
        assert data_response_task['status'] == test_create_task['status']
    
    @pytest.mark.asyncio
    async def test_update_status_current_task_partial(self, httpx_client: AsyncClient, test_create_task: dict):
        url = f'/api/v1/task/{test_create_task["id"]}/'
        await self.wait_for_server(url)
        assert test_create_task is not None
        response = await httpx_client.patch(url, json={
            'status': 'in_progress', 
        })
        assert response.status_code == status.HTTP_200_OK
        data_response_task = response.json()
        assert data_response_task['id'] == test_create_task['id']
        assert data_response_task['title'] == test_create_task['title']
        assert data_response_task['description'] == test_create_task['description']
        assert data_response_task['status'] == 'in_progress'
    
    @pytest.mark.asyncio
    async def test_update_failed_id_task_partial(self, httpx_client: AsyncClient):
        url = '/api/v1/task/1/'
        await self.wait_for_server(url)
        response = await httpx_client.patch(url, json={
            'title': 'Update Task', 
            'description': None,
            'status': 'in_progress',
        })
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_delete_current_task(self, httpx_client: AsyncClient, test_create_task: dict):
        url = f'/api/v1/task/{test_create_task["id"]}/'
        await self.wait_for_server(url)
        assert test_create_task is not None
        response = await httpx_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    @pytest.mark.asyncio
    async def test_delete_failed_id_task(self, httpx_client: AsyncClient):
        url = '/api/v1/task/1/'
        await self.wait_for_server(url)
        response = await httpx_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        

    

    

    