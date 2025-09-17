from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from infrastructure.database.models import Task
from infrastructure.database.models.task import TaskStatus
from api_v1.rest.tasks.schemas import (
    TaskCreate,
    SchemaTask,
    TaskUpdate,
    TaskUpdatePartial,
    TasksResponseSchema,
)
import logging.config
from core.logger import logger_config

logging.config.dictConfig(logger_config)
logger = logging.getLogger('task_repository_logger')


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        stmt = select(Task).where(Task.id == task_id)
        result = await self.session.execute(stmt)
        return result.scalars().one_or_none()
    
    async def get_tasks(
        self,
        column: str = 'title',
        sort: str = 'desc',
        page: int = 1,
        limit: int = 10,
        column_search: str | None = None,
        input_search: str | None = None,
    ) -> TasksResponseSchema:
        stmt = select(Task)
        total_stmt = select(func.count(Task.id))

        if column_search and input_search:
            if column_search in ('title', 'description'):
                input_column = getattr(Task, column_search)
                stmt = stmt.where(input_column.like(input_search + '%'))
                total_stmt = total_stmt.where(input_column.like(input_search + '%'))

            elif column_search == 'status':
                if input_search.upper() == 'CREATED':
                    stmt = stmt.where(Task.status == TaskStatus.CREATED)
                elif input_search.upper() == 'IN_PROGRESS':
                    stmt = stmt.where(Task.status == TaskStatus.IN_PROGRESS)
                elif input_search.upper() == 'COMPLETED':
                    stmt = stmt.where(Task.status == TaskStatus.COMPLETED)
                else:
                    logger.exception('Неизвестный статус задачи: %s', input_search)
                    raise ValueError(f'Неизвестный статус задачи: {input_search}')

        total_result = await self.session.execute(total_stmt)
        total_tasks = total_result.scalar() or 0

        # Вычисляем количество страниц
        pages_count = (total_tasks + limit - 1) // limit  # Округление вверх
        # Добавляем пагинацию к запросу
        offset = (page - 1) * limit

        task_column = getattr(Task, column)
        # определяем направление сортировки
        ordering = task_column.desc() if sort.lower() == 'desc' else task_column.asc()
        # строим запрос с сортировкой, лимитом и offset
        stmt = stmt.order_by(ordering).limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        tasks = result.scalars().all()
        if tasks is None:
            tasks = []
        return TasksResponseSchema(
            pages_count=pages_count,
            total=total_tasks,
            tasks=tasks,
        )
    
    async def create_task(
        self,
        task: TaskCreate,
    ) -> Optional[SchemaTask]:
        task = Task(**task.model_dump())
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def update_task(
        self,
        task: Task,
        task_update: TaskUpdate | TaskUpdatePartial,
        partial: bool = False,
    ) -> Optional[Task]:
        for name, value in task_update.model_dump(exclude_unset=partial).items():
            if name == 'status' and isinstance(value, str):
                value = TaskStatus(task_update.status)
            setattr(task, name, value)
        await self.session.flush()
        await self.session.refresh(task)
        return task
        
    async def delete_task(
        self,
        task: Task,
    ) -> None:
        await self.session.delete(task)
        await self.session.flush()

