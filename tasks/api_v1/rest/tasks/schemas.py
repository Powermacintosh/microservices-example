from pydantic import BaseModel, ConfigDict
from typing import Annotated, List
from annotated_types import MinLen, MaxLen
from enum import Enum


class TaskStatusEnum(str, Enum):
    CREATED = 'created'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'

class TaskBase(BaseModel):
    title: Annotated[str, MinLen(1), MaxLen(100)]
    description: Annotated[str | None, MaxLen(255)] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskCreate):
    status: TaskStatusEnum

class TaskUpdatePartial(TaskUpdate):
    title: str | None = None
    description: str | None = None
    status: TaskStatusEnum | None = None

class SchemaTask(TaskUpdate):
    model_config = ConfigDict(from_attributes=True)
    
    id: str

class BaseTasksResponseSchema(BaseModel):
    pages_count: int
    total: int

class TasksResponseSchema(BaseTasksResponseSchema):
    tasks: List[SchemaTask]