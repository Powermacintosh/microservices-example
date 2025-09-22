import pytest, asyncio, httpx
from typing import Dict, Any, Optional
from httpx import AsyncClient
from core.config import settings


class TestTaskGraphQLAPI:
    """
    Тесты для GraphQL API менеджера задач.
    """
    
    GRAPHQL_ENDPOINT = '/api/v1/graphql'
    
    async def wait_for_server(self, url: str, timeout: int = 30) -> bool:
        """Ожидает подключения к серверу."""
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

    async def execute_graphql_query(
        self, 
        httpx_client: AsyncClient, 
        query: str, 
        variables: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Выполняет GraphQL запрос и возвращает ответ."""
        response = await httpx_client.post(
            self.GRAPHQL_ENDPOINT,
            json={
                'query': query,
                'variables': variables or {}
            },
            headers=headers or {}
        )
        return response.json()

    @pytest.fixture
    async def test_create_task(self, httpx_client: AsyncClient) -> Dict[str, Any]:
        """Фикстура для создания тестовой задачи через GraphQL."""
        await self.wait_for_server(self.GRAPHQL_ENDPOINT)
        
        create_mutation = """
        mutation CreateTask($input: TaskCreateInputGQL!) {
            createTask(input: $input) {
                id
                title
                description
                status
            }
        }
        """
        variables = {
            'input': {
                'title': 'Test Task',
                'description': 'Test Description'
            }
        }
        response = await self.execute_graphql_query(
            httpx_client, 
            create_mutation, 
            variables=variables
        )
        
        assert 'data' in response, f'Ошибка при создании задачи: {response}'
        assert 'createTask' in response['data'], f'Ошибка в ответе: {response}'
        
        task = response['data']['createTask']
        assert task['title'] == 'Test Task'
        assert task['description'] == 'Test Description'
        assert task['status'] == 'CREATED'
        
        return task
    
    @pytest.mark.asyncio
    async def test_get_task(self, httpx_client: AsyncClient, test_create_task: Dict[str, Any]):
        """Тест получения задачи по ID."""
        task_id = test_create_task['id']
        
        query = """
        query GetTask($id: ID!) {
            task(id: $id) {
                id
                title
                description
                status
            }
        }
        """
        
        response = await self.execute_graphql_query(
            httpx_client,
            query,
            variables={'id': task_id}
        )
        
        assert 'data' in response, f'Ошибка при получении задачи: {response}'
        assert 'task' in response['data'], f'Ошибка в ответе: {response}'
        
        task = response['data']['task']
        assert task['id'] == task_id
        assert task['title'] == 'Test Task'
        assert task['description'] == 'Test Description'
        assert task['status'] == 'CREATED'
    
    @pytest.mark.asyncio
    async def test_get_tasks_list(self, httpx_client: AsyncClient, test_create_task: Dict[str, Any]):
        """Тест получения списка задач."""
        query = """
        query GetTasks($status: TaskStatusGQL, $offset: Int, $limit: Int) {
            tasks(status: $status, offset: $offset, limit: $limit) {
                tasks {
                    id
                    title
                    status
                }
                total
                pagesCount
            }
        }
        """
        
        # Получаем все задачи
        response = await self.execute_graphql_query(
            httpx_client,
            query,
            variables={'status': 'CREATED', 'offset': 0, 'limit': 10}
        )
        
        assert 'data' in response, f'Ошибка при получении списка задач: {response}'
        assert 'tasks' in response['data'], f'Ошибка в ответе: {response}'
        
        tasks_page = response['data']['tasks']
        assert isinstance(tasks_page['tasks'], list)
        assert tasks_page['total'] > 0
        assert tasks_page['pagesCount'] > 0
        
        # Проверяем, что созданная задача есть в списке
        task_ids = [task['id'] for task in tasks_page['tasks']]
        assert test_create_task['id'] in task_ids
    
    @pytest.mark.asyncio
    async def test_update_task(self, httpx_client: AsyncClient, test_create_task: Dict[str, Any]):
        """Тест обновления задачи."""
        task_id = test_create_task['id']
        
        update_mutation = """
        mutation UpdateTask($id: ID!, $input: TaskUpdateInputGQL!) {
            updateTask(id: $id, input: $input) {
                id
                title
                description
                status
            }
        }
        """
        
        variables = {
            'id': task_id,
            'input': {
                'title': 'Updated Task',
                'description': 'Updated Description',
                'status': 'IN_PROGRESS'
            }
        }
        
        response = await self.execute_graphql_query(
            httpx_client,
            update_mutation,
            variables=variables
        )
        
        assert 'data' in response, f'Ошибка при обновлении задачи: {response}'
        assert 'updateTask' in response['data'], f'Ошибка в ответе: {response}'
        
        updated_task = response['data']['updateTask']
        assert updated_task['id'] == task_id
        assert updated_task['title'] == 'Updated Task'
        assert updated_task['description'] == 'Updated Description'
        assert updated_task['status'] == 'IN_PROGRESS'
    
    @pytest.mark.asyncio
    async def test_delete_task(self, httpx_client: AsyncClient, test_create_task: Dict[str, Any]):
        """Тест удаления задачи."""
        task_id = test_create_task['id']
        
        delete_mutation = """
        mutation DeleteTask($id: ID!) {
            deleteTask(id: $id)
        }
        """
        
        # Удаляем задачу
        response = await self.execute_graphql_query(
            httpx_client,
            delete_mutation,
            variables={'id': task_id}
        )
        
        assert 'data' in response, f'Ошибка при удалении задачи: {response}'
        assert 'deleteTask' in response['data'], f'Ошибка в ответе: {response}'
        assert response['data']['deleteTask'] is True
        
        # Проверяем, что задача действительно удалена
        query = """
        query GetTask($id: ID!) {
            task(id: $id) {
                id
            }
        }
        """
        
        response = await self.execute_graphql_query(
            httpx_client,
            delete_mutation,
            variables={'id': task_id}
        )
        assert response['data']['deleteTask'] is False

        response = await self.execute_graphql_query(
            httpx_client,
            query,
            variables={'id': task_id}
        )
        
        # Задача не должна быть найдена
        assert 'data' in response, f'Ошибка при проверке удаления задачи: {response}'
        assert response['data']['task'] is None
