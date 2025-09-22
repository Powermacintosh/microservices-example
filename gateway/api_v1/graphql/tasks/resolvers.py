import strawberry, httpx
from .schemas import (
    TaskGQL,
    TaskPageGQL,
    TaskCreateInputGQL,
    TaskUpdateInputGQL,
    TaskStatusGQL,
    map_json_to_task_gql
)
from ..query_loader import load_query, load_mutation
from typing import Optional
from core.config import settings

TASKS_URL = settings.tasks_microservice_url + '/api/v1/graphql'

@strawberry.type
class Query:
    @strawberry.field
    async def task(
        self,
        id: strawberry.ID,
    ) -> Optional[TaskGQL]: 
        query = load_query('get_task', 'tasks')
        async with httpx.AsyncClient() as client:
            resp = await client.post(TASKS_URL, json={'query': query, 'variables': {'id': id}})
            data = resp.json()['data']['task']
            if data is None:
                return None
            return map_json_to_task_gql(data)

    @strawberry.field
    async def tasks(
        self,
        status: Optional[TaskStatusGQL] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> TaskPageGQL:
        """
        Получение списка задач с поддержкой:
        - Фильтрации по статусу
        - Пагинации (offset/limit)
        """
        query = load_query('get_tasks', 'tasks')
        async with httpx.AsyncClient() as client:
            variables = {
                'offset': offset,
                'limit': limit
            }
            if status:
                variables['status'] = status.value.upper()
            response = await client.post(
                TASKS_URL,
                json={
                    'query': query,
                    'variables': variables
                }
            )
            data = response.json()
            if 'errors' in data:
                error_msg = data['errors'][0]['message']
                raise Exception(f'Ошибка получения задач: {error_msg}')
            tasks_data = data['data']['tasks']
            return TaskPageGQL(
                tasks=[
                    map_json_to_task_gql(task)
                    for task in tasks_data['tasks']
                ],
                total=tasks_data['total'],
                pages_count=tasks_data['pagesCount']
            )

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_task(
        self,
        input: TaskCreateInputGQL,
    ) -> TaskGQL:
        """Создание новой задачи"""
        query = load_mutation('create_task', 'tasks')
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TASKS_URL,
                json={
                    'query': query,
                    'variables': {
                        'title': input.title,
                        'description': input.description
                    }
                }
            )
            data = response.json()
            if 'errors' in data:
                error_msg = data['errors'][0]['message']
                raise Exception(f'Ошибка создания задачи: {error_msg}')
            task_data = data['data']['createTask']
            return map_json_to_task_gql(task_data)

    @strawberry.mutation
    async def update_task(
        self,
        id: strawberry.ID,
        input: TaskUpdateInputGQL,
    ) -> Optional[TaskGQL]:
        """Обновление задачи"""
        query = load_mutation('update_task', 'tasks')
        update_data = input.to_dict()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TASKS_URL,
                json={
                    'query': query,
                    'variables': {
                        'id': id,
                        'input': update_data
                    }
                }
            )
            data = response.json()
            if 'errors' in data:
                error_msg = data['errors'][0]['message']
                raise Exception(f'Ошибка обновления задачи: {error_msg}')
            task_data = data['data']['updateTask']
            return map_json_to_task_gql(task_data) if task_data else None

    @strawberry.mutation
    async def delete_task(
        self,
        id: strawberry.ID,
    ) -> bool:
        """Удаление задачи"""
        query = load_mutation('delete_task', 'tasks')
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TASKS_URL,
                json={
                    'query': query,
                    'variables': {
                        'id': id
                    }
                }
            )
            data = response.json()
            if 'errors' in data:
                error_msg = data['errors'][0]['message']
                raise Exception(f'Ошибка удаления задачи: {error_msg}')
            return bool(data['data']['deleteTask'])
