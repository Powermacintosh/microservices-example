from infrastructure.external_service_facade import ExternalServiceFacade
from core.config import settings
from api_v1.rest.tasks.schemas import (
    TaskUpdate,
    TaskUpdatePartial,
    TaskCreate,
)


class TaskFacade:
    def __init__(self, base_url: str):
        self.external_facade = ExternalServiceFacade(base_url=base_url)

    async def get_tasks(
        self,
        # filters: TaskFilters,
        column: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        column_search: str | None = None,
        input_search: str | None = None,
    ):
        params = {
            'column': column,
            'sort': sort,
            'page': page,
            'limit': limit,
            'column_search': column_search,
            'input_search': input_search,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        return await self.external_facade.proxy_endpoint(endpoint='tasks/', data=params)

    async def get_task(self, task_id: int):
        return await self.external_facade.proxy_endpoint(endpoint=f'task/{task_id}/')
    
    async def create_task(self, task: TaskCreate):
        return await self.external_facade.proxy_endpoint(endpoint='task/create', data=task, method='post')

    async def update_task(self, task_id: int, task_update: TaskUpdate):
        return await self.external_facade.proxy_endpoint(endpoint=f'task/{task_id}/', data=task_update, method='put')
    
    async def update_partial_task(self, task_id: int, task_update: TaskUpdatePartial):
        return await self.external_facade.proxy_endpoint(endpoint=f'task/{task_id}/', data=task_update, method='patch')
     
    async def delete_task(self, task_id: int):
        return await self.external_facade.proxy_endpoint(endpoint=f'task/{task_id}/', method='delete')

task_facade = TaskFacade(base_url=settings.tasks_microservice_url)