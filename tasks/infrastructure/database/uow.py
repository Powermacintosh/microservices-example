from contextlib import asynccontextmanager
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from core.repositories.task import TaskRepository
from .db_connect import async_session
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError,
    OperationalError,
    TimeoutError
)
from fastapi import HTTPException

import logging.config
from core.logger import logger_config

logging.config.dictConfig(logger_config)
logger = logging.getLogger('database_logger')

class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
        # доступ ко всем репозиториям
        self.tasks: TaskRepository = TaskRepository(self.session)

    async def commit(self) -> None:
        await self.session.commit()
        
    async def rollback(self) -> None:
        await self.session.rollback()

    async def close(self) -> None:
        await self.session.close()

@asynccontextmanager
async def unit_of_work() -> AsyncIterator[UnitOfWork]:
    """Контекстный менеджер для работы с Unit of Work"""
    session = async_session()
    uow = UnitOfWork(session)
    try:
        yield uow
        await uow.commit()
    except IntegrityError as e:
        await uow.rollback()
        logger.exception('Unit of work: Ошибка целостности данных', exc_info=e)
        raise ValueError('UOW: Ошибка: нарушение целостности данных') from e
    except OperationalError as e:
        await uow.rollback()
        logger.exception('Unit of work: Ошибка подключения к БД', exc_info=e)
        raise ConnectionError('UOW: Ошибка подключения к базе данных') from e
    except TimeoutError as e:
        await uow.rollback()
        logger.exception('Unit of work: Таймаут операции с БД', exc_info=e)
        raise TimeoutError('UOW: Превышено время ожидания ответа от БД') from e
    except SQLAlchemyError as e:
        await uow.rollback()
        logger.exception('Unit of work: Ошибка выполнения запроса', exc_info=e)
        raise RuntimeError('UOW: Ошибка при выполнении запроса к БД') from e
    except Exception as e:
        if isinstance(e, HTTPException) and getattr(e, 'status_code', 404) == 404:
            # Пропускаем исключения и передаём вверх по стеку вызовов
            logger.debug('Unit of work: пропускаем бизнес/клиентскую ошибку', exc_info=e)
            raise
        await uow.rollback()
        logger.critical('Unit of work: Непредвиденная ошибка', exc_info=e)
        raise
    finally:
        await uow.close()
