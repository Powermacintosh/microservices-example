from typing import Annotated
from fastapi import APIRouter, Depends, status, Path
from .dependencies import (
    get_task_service,
    task_by_id,
    AIOKafkaProducer,
    get_producer
)
from .service import TaskService
from infrastructure.database.models import Task
from .schemas import (
    TaskCreate,
    SchemaTask,
    TaskUpdate,
    TaskUpdatePartial,
    TasksResponseSchema
)
# from infrastructure.kafka.producer import producer
from core.config import settings

import logging.config
from core.logger import logger_config

logging.config.dictConfig(logger_config)
kafka_logger = logging.getLogger('kafka_logger')

router, router_list = APIRouter(tags=['Tasks']), APIRouter(tags=['Tasks'])


@router.post('/create', response_model=SchemaTask, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    service: TaskService = Depends(get_task_service),
    ):
    """Создает новую задачу.

    | Параметр | Тип         | Описание                               |
    |----------|-------------|----------------------------------------|
    | task     | TaskCreate  | Задача, которую нужно создать.         |

    Возвращает:
        SchemaTask: Созданная задача. `201`

    Исключения:
        HTTPException: При возникновении ошибки.
    """
    return await service.create_task(task=task)


@router.get('/{task_id}/', response_model=SchemaTask, status_code=status.HTTP_200_OK)
async def get_task(task: SchemaTask = Depends(task_by_id)):
    """
    Получает задачу по ID.

    | Параметр | Тип         | Описание                               |
    |----------|-------------|----------------------------------------|
    | task     | SchemaTask  | Задача, которую нужно получить.        |

    Возвращает:
        SchemaTask: Задача. `200`
    
    Исключения:
        HTTPException: При возникновении ошибки.
    """
    return task


@router.put('/{task_id}/', response_model=SchemaTask, status_code=status.HTTP_200_OK)
async def update_task(
    task_update: TaskUpdate,
    task: Task = Depends(task_by_id),
    service: TaskService = Depends(get_task_service),
):
    """
    Полностью обновляет задачу по ID.

    | Параметр    | Тип           | Описание                                |
    |-------------|---------------|-----------------------------------------|
    | task        | SchemaTask    | Задача, которую нужно обновить.         |
    
    Возвращает:
        SchemaTask: Обновленная задача. `200`
    
    Исключения:
        HTTPException: При возникновении ошибки.
    """
    return await service.update_task(
        task=task,
        task_update=task_update
    )


@router.patch('/{task_id}/', response_model=SchemaTask, status_code=status.HTTP_200_OK)
async def update_partial_task(
    task_update: TaskUpdatePartial,
    task: Task = Depends(task_by_id),
    service: TaskService = Depends(get_task_service),
):
    """
    Частично обновляет задачу по ID.

    | Параметр    | Тип                   | Описание                                |
    |-------------|-----------------------|-----------------------------------------|
    | task        | SchemaTask            | Задача, которую нужно обновить.         |
    
    Возвращает:
        SchemaTask: Обновленная задача. `200`
    
    Исключения:
        HTTPException: При возникновении ошибки.
    """
    return await service.update_task(
        task=task,
        task_update=task_update,
        partial=True,
    )


@router.delete('/{task_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task: Task = Depends(task_by_id),
    service: TaskService = Depends(get_task_service),
):
    """
    Удаляет задачу по ID.

    | Параметр    | Тип           | Описание                                |
    |-------------|---------------|-----------------------------------------|
    | task        | SchemaTask    | Задача, которую нужно удалить.          |
    
    Возвращает:
        None: `204`
    
    Исключения:
        HTTPException: При возникновении ошибки.
    """
    return await service.delete_task(task=task)


@router_list.get('/', response_model=TasksResponseSchema, status_code=status.HTTP_200_OK)
async def get_list_tasks(
    column: str | None = 'title',
    sort: str | None = 'desc',
    page: int | None = 1,
    limit: int | None = 10,
    column_search: str | None = None,
    input_search: str | None = None,
    service: TaskService = Depends(get_task_service),
):
    """
    Получает список задач.

    | Параметр      | Тип           | Описание                                |
    |---------------|---------------|-----------------------------------------|
    | column_search | str           | Поле для поиска.                        |
    | input_search  | str           | Значение для поиска.                    |
    | column        | str           | Поле для сортировки.                    |
    | sort          | str           | Направление сортировки.                 |
    | page          | int           | Номер страницы.                         |
    | limit         | int           | Количество задач на странице.           |
    
    Возвращает:
        TasksResponseSchema: Список задач c пагинацией. `200`
    
    Исключения:
        HTTPException: При возникновении ошибки.
    """
    return await service.get_tasks(
        column=column,
        sort=sort,
        page=page,
        limit=limit,
        column_search=column_search,
        input_search=input_search,
    )

@router.post('/create_event', status_code=status.HTTP_201_CREATED)
async def send_task_creation_event(
    task: TaskCreate,
    producer: AIOKafkaProducer = Depends(get_producer)
):
    event = {
        'event': 'TaskModuleCreation',
        'task': task.model_dump()
    }
    try:
        await producer.send_and_wait(topic=settings.kafka.TOPIC, value=event)
        kafka_logger.info('Сообщение успешно отправлено в topic task_events')
    except Exception as e:
        kafka_logger.exception('Ошибка отправки сообщения в topic task_events', exc_info=e)
        raise HTTPException(status_code=503, detail=f'Ошибка отправки сообщения в topic task_events: {e}')
    return {'status': 'published'}