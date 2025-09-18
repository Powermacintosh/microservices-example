from typing import Annotated, AsyncIterator
from fastapi import Path, Depends
from infrastructure.database.uow import UnitOfWork, unit_of_work
from .service import TaskService

from infrastructure.database.models import Task
from .decorators import handle_errors
from .exceptions import TaskNotFoundException
from aiokafka import AIOKafkaProducer


async def get_producer() -> AIOKafkaProducer:
    from main import app
    return app.state.kafka_producer

async def get_uow() -> AsyncIterator[UnitOfWork]:
    async with unit_of_work() as uow:
        yield uow

def get_task_service(uow: UnitOfWork = Depends(get_uow)) -> TaskService:
    return TaskService(uow)

@handle_errors
async def task_by_id(
    task_id: Annotated[str, Path],
    service: TaskService = Depends(get_task_service),
) -> Task:
    """
    Получает задачу по ID.

    param task_id: ID задачи, которую нужно получить.
    return: Задача, если найдена.
    raises HTTPException: Если задача не найдена.
    """
    task = await service.get_task(task_id=task_id)
    if task is None:
        raise TaskNotFoundException(task_id)
    return task