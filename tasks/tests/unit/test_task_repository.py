import pytest
from sqlalchemy import select
from typing import AsyncIterator

from infrastructure.database.models.task import Task, TaskStatus
from infrastructure.database.repositories.task import TaskRepository
from api_v1.rest.tasks.schemas import TaskCreate, TaskUpdate, TaskUpdatePartial

class TestTaskRepository:
    """Тесты для TaskRepository"""
    
    @pytest.mark.asyncio
    async def test_search_failed_task(self, testing_db_connection: AsyncIterator):
        """Тест поиска задач по названию с реальным сохранением в БД"""
        repo = TaskRepository(testing_db_connection.session)
        result = await repo.get_task(task_id='1')
        assert result is None
    
    @pytest.mark.asyncio
    async def test_create_and_get_task(self, testing_db_connection: AsyncIterator):
        repo = TaskRepository(testing_db_connection.session)

        task = TaskCreate(title='Test task')
        new_task = await repo.create_task(task)

        fetched = await repo.get_task(new_task.id)

        assert fetched is not None
        assert fetched.title == 'Test task'
    
    @pytest.mark.asyncio
    async def test_update_task(self, testing_db_connection: AsyncIterator):
        repo = TaskRepository(testing_db_connection.session)
        
        task = TaskCreate(title='Test task')
        new_task = await repo.create_task(task)
        
        updated_task = await repo.update_task(new_task, 
            TaskUpdate(
                title='Updated task',
                description='Updated description',
                status=TaskStatus.IN_PROGRESS
            )
        )
        assert updated_task.title == 'Updated task' 
        assert updated_task.description == 'Updated description'
        assert updated_task.status == TaskStatus.IN_PROGRESS
    
    @pytest.mark.asyncio
    async def test_update_task_partial(self, testing_db_connection: AsyncIterator):
        repo = TaskRepository(testing_db_connection.session)
        
        task = TaskCreate(title='Test task')
        new_task = await repo.create_task(task)
        
        updated_task = await repo.update_task(
            task=new_task, 
            task_update=TaskUpdatePartial(
                title='Updated Partial task',
            ),
            partial=True,
        )
        assert updated_task.title == 'Updated Partial task' 
        assert updated_task.description == None
        assert updated_task.status == TaskStatus.CREATED
    
    @pytest.mark.asyncio
    async def test_delete_task(self, testing_db_connection: AsyncIterator):
        repo = TaskRepository(testing_db_connection.session)
        
        task = TaskCreate(title='Test task')
        new_task = await repo.create_task(task)

        new_task_fetched = await repo.get_task(task_id=new_task.id)
        assert new_task_fetched.id == new_task.id
        assert new_task_fetched.title == 'Test task'
        assert new_task_fetched.description == None
        assert new_task_fetched.status == TaskStatus.CREATED

        stmt = select(Task).where(Task.id == new_task.id)
        result = await testing_db_connection.session.execute(stmt)
        db_task = result.scalars().one_or_none()
        assert db_task.id == new_task.id
        assert db_task.title == new_task.title
        assert db_task.description == new_task.description
        assert db_task.status == new_task.status
        
        deleted_task = await repo.delete_task(task=new_task)
        assert deleted_task is None

        fetched = await repo.get_task(task_id=new_task.id)
        assert fetched is None

        stmt = select(Task).where(Task.id == new_task.id)
        result = await testing_db_connection.session.execute(stmt)
        deleted_task = result.scalars().one_or_none()
        assert deleted_task is None
    
    @pytest.mark.asyncio
    async def test_get_list_tasks(self, testing_db_connection: AsyncIterator):
        repo = TaskRepository(testing_db_connection.session)
        
        task_1 = TaskCreate(title='Test task')
        new_task_1 = await repo.create_task(task_1)

        task_2 = TaskCreate(title='Test task 2')
        new_task_2 = await repo.create_task(task_2)

        fetched = await repo.get_tasks(limit=1000)
        ids = [task.id for task in fetched.tasks]
        assert new_task_1.id in ids
        assert new_task_2.id in ids