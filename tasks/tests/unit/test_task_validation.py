import pytest
from sqlalchemy import exc
from typing import AsyncIterator
from pydantic import ValidationError
from core.repositories.task import TaskRepository
from api_v1.rest.tasks.schemas import TaskCreate

class TestTaskPydanticValidation:
    """Тесты валидации данных задачи."""
    
    @pytest.mark.asyncio
    async def test_pydantic_create_failed_max_length_title_task(self, testing_db_connection: AsyncIterator):
        repo = TaskRepository(testing_db_connection.session)
        
        # Теперь Pydantic выбросит ValidationError при создании модели
        with pytest.raises(ValidationError) as exc_info:
            task = TaskCreate(title='Test task' * 100)
            await repo.create_task(task)
        
        # Проверяем, что ошибка связана с превышением максимальной длины
        assert 'String should have at most 100 characters' in str(exc_info.value)


class TestTaskDatabaseValidation:
    """Тесты валидации данных задачи."""

    @pytest.mark.asyncio
    async def test_dbapi_create_failed_max_length_title_task(self, testing_db_connection: AsyncIterator):
        repo = TaskRepository(testing_db_connection.session)
        
        task = TaskCreate(title='Test task')
        task.title = 'Test task' * 100
        # Ожидаем, что при сохранении выбросится DBAPIError
        with pytest.raises(exc.DBAPIError) as exc_info:
            await repo.create_task(task)
        
        # Проверяем, что в сообщении об ошибке есть информация о превышении длины
        assert 'value too long for type character varying(100)' in str(exc_info.value)

        # Явно откатываем транзакцию после ошибки
        await testing_db_connection.rollback()