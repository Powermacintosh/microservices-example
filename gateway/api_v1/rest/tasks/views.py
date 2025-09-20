from fastapi import APIRouter,Query, status, Path, Depends
from typing import Annotated
from .schemas import (
    SchemaTask,
    TaskCreate,
    TaskUpdate,
    TaskUpdatePartial,
    TasksResponseSchema,
    TaskFilters
)
from infrastructure.tasks_facade import task_facade
from .dependencies import AIOKafkaProducer, get_producer
from core.config import settings

import logging.config
from core.logger import logger_config

logging.config.dictConfig(logger_config)
kafka_logger = logging.getLogger('kafka_logger')

router, router_list, router_worker = APIRouter(tags=['Tasks']), APIRouter(tags=['Tasks']), APIRouter(tags=['Task Worker Events'])


@router.get('/{task_id}/', response_model=SchemaTask, status_code=status.HTTP_200_OK)
async def get_task(task_id: Annotated[str, Path]):
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
    return await task_facade.get_task(task_id=task_id)

@router.post('/create', response_model=SchemaTask, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    """Создает новую задачу.

    | Параметр | Тип         | Описание                               |
    |----------|-------------|----------------------------------------|
    | task     | TaskCreate  | Задача, которую нужно создать.         |

    Возвращает:
        SchemaTask: Созданная задача. `201`

    Исключения:
        HTTPException: При возникновении ошибки.
    """
    return await task_facade.create_task(task=task)


@router.put('/{task_id}/', response_model=SchemaTask, status_code=status.HTTP_200_OK)
async def update_task(
    task_update: TaskUpdate,
    task_id: Annotated[str, Path],
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
    return await task_facade.update_task(
        task_id=task_id,
        task_update=task_update
    )


@router.patch('/{task_id}/', response_model=SchemaTask, status_code=status.HTTP_200_OK)
async def update_partial_task(
    task_update: TaskUpdatePartial,
    task_id: Annotated[str, Path]
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
    return await task_facade.update_partial_task(
        task_id=task_id,
        task_update=task_update,
    )


@router.delete('/{task_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: Annotated[str, Path]):
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
    return await task_facade.delete_task(task_id=task_id)

@router_list.get('/', response_model=TasksResponseSchema, status_code=status.HTTP_200_OK)
async def get_list_tasks(
    filters: TaskFilters = Query(
        default=...,
        description='Параметры фильтрации и пагинации',
        openapi_examples={
            'default': {
                'summary': 'Стандартные параметры',
                'description': 'Получение первой страницы с 10 задачами, отсортированными по убыванию даты создания',
                'value': {
                    'column': 'created_at',
                    'sort': 'desc',
                    'page': 1,
                    'limit': 10
                }
            },
            'search': {
                'summary': 'Поиск задач',
                'description': 'Поиск задач по заголовку',
                'value': {
                    'column_search': 'title',
                    'input_search': 'срочно',
                    'page': 1,
                    'limit': 20
                }
            }
        }
    )
) -> TasksResponseSchema:
    """
    Получает список задач с возможностью фильтрации, сортировки и пагинации.
    
    Параметры:
    - **column**: Поле для сортировки (по умолчанию 'title')
    - **sort**: Направление сортировки: 'asc' (по возрастанию) или 'desc' (по убыванию)
    - **page**: Номер страницы (начинается с 1)
    - **limit**: Количество записей на странице (максимум 100)
    - **column_search**: Поле для поиска (опционально)
    - **input_search**: Значение для поиска (опционально, используется с column_search)
    
    Возвращает:
        TasksResponseSchema: Список задач с метаданными пагинации.
    
    Исключения:
        HTTPException 400: Некорректные параметры запроса.
        HTTPException 500: Ошибка сервера при обработке запроса.
    """
    return await task_facade.get_tasks(
        column=filters.column,
        sort=filters.sort,
        page=filters.page,
        limit=filters.limit,
        column_search=filters.column_search,
        input_search=filters.input_search,
    )

@router_worker.post('/create_event', status_code=status.HTTP_201_CREATED)
async def send_task_creation_event(
    task: TaskCreate,
    producer: AIOKafkaProducer = Depends(get_producer)
):
    event = {
        'event': 'TaskCreation',
        'task': task.model_dump()
    }
    try:
        await producer.send_and_wait(topic=settings.kafka.TOPIC, value=event)
        kafka_logger.info('Сообщение успешно отправлено', extra={
            'tags': {
                'topic': settings.kafka.TOPIC,
                'event': event['event'],
                'task_title': event['task']['title'],
                'task_description': event['task']['description'],
            }
        })
    except Exception as e:
        kafka_logger.exception('Ошибка отправки сообщения в topic task_events', exc_info=e)
        raise HTTPException(status_code=503, detail=f'Ошибка отправки сообщения в topic task_events: {e}')
    return {'status': 'published'}
