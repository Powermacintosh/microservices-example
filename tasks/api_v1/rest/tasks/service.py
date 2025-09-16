from infrastructure.database.models import Task
from .schemas import (
    TaskCreate,
    SchemaTask,
    TaskUpdate,
    TaskUpdatePartial,
    TasksResponseSchema,
)
from typing import Optional
from infrastructure.database.uow import UnitOfWork


class TaskService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    async def create_task(self, task: TaskCreate) -> Optional[SchemaTask]:
        return await self.uow.tasks.create_task(task)
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        return await self.uow.tasks.get_task(task_id)

    async def get_tasks(
        self,
        column: str = 'title',
        sort: str = 'desc',
        page: int = 1,
        limit: int = 10,
        column_search: str | None = None,
        input_search: str | None = None,
    ) -> TasksResponseSchema:
        return await self.uow.tasks.get_tasks(
            column=column,
            sort=sort,
            page=page,
            limit=limit,
            column_search=column_search,
            input_search=input_search,
        )

    async def update_task(
        self,
        task: SchemaTask,
        task_update: TaskUpdate | TaskUpdatePartial,
        partial: bool = False,
    ) -> Optional[Task]:
        return await self.uow.tasks.update_task(
            task=task,
            task_update=task_update,
            partial=partial,
        )

    async def delete_task(
        self,
        task: SchemaTask,
    ) -> None:
        return await self.uow.tasks.delete_task(task)
        