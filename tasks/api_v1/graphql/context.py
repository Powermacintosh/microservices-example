from typing import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import Request
from strawberry.fastapi import BaseContext
from infrastructure.database.uow import UnitOfWork, unit_of_work
from api_v1.service.task import TaskService


class GraphQLContext(BaseContext):
    def __init__(
        self,
        request: Request,
        uow: UnitOfWork,
        task_service: TaskService,
    ):
        self.request = request
        self.uow = uow
        self.task_service = task_service

@asynccontextmanager
async def get_context(request: Request) -> AsyncIterator[GraphQLContext]:
    """Контекст для GraphQL запросов, использующий существующий Unit of Work"""
    async with unit_of_work() as uow:
        task_service = TaskService(uow)
        yield GraphQLContext(
            request=request,
            uow=uow,
            task_service=task_service,
        )

# Сохранение межзапросного контекста для GraphQL
async def get_context_wrapper(request: Request):
    async with get_context(request) as ctx:
        yield ctx
