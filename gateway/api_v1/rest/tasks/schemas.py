from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Annotated, List, Optional, Literal
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

class TaskFilters(BaseModel):
    """Модель для фильтрации и пагинации задач."""
    column: str = Field(
        default='title',
        description='Поле для сортировки',
        examples=['title', 'created_at']
    )
    sort: Literal['asc', 'desc'] = Field(
        default='desc',
        description='Направление сортировки: asc (по возрастанию) или desc (по убыванию)',
        examples=['desc']
    )
    page: int = Field(
        default=1,
        ge=1,
        description='Номер страницы (начинается с 1)',
        examples=[1]
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description='Количество записей на странице (максимум 100)',
        examples=[10]
    )
    column_search: Optional[str] = Field(
        default=None,
        description='Поле для поиска',
        examples=['title', 'description']
    )
    input_search: Optional[str] = Field(
        default=None,
        description='Значение для поиска',
        examples=['важная задача']
    )

    @field_validator('column')
    @classmethod
    def validate_column(cls, v):
        allowed_columns = ['title', 'created_at', 'updated_at', 'status']
        if v not in allowed_columns:
            raise ValueError(f'Допустимые значения для сортировки: {", ".join(allowed_columns)}')
        return v
