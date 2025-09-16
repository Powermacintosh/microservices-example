from contextlib import asynccontextmanager
from typing import AsyncIterator
from .exceptions import DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession
from .repositories.task import TaskRepository
from .db_connect import async_session


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
    except DatabaseError as e:
        await uow.rollback()
        raise DatabaseError.from_sqlalchemy(e, 'unit of work') from e
    except Exception as e:
        await uow.rollback()
        raise e
    finally:
        await uow.close()
