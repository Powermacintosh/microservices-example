from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Enum as PgEnum
from enum import Enum

from .base import Base

class TaskStatus(Enum):
    CREATED = 'created'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'

class Task(Base):
    __tablename__ = 'tasks'

    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[TaskStatus] = mapped_column(PgEnum(TaskStatus, name='task_status_enum'), default=TaskStatus.CREATED)


    
    
   