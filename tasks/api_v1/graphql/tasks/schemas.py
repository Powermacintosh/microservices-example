import strawberry
from enum import Enum
from typing import Optional, List
from core.models.task import TaskStatus
from core.models import Task


@strawberry.enum
class TaskStatusGQL(str, Enum):
    CREATED = 'created'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'

def map_to_task_status(status: TaskStatusGQL) -> TaskStatus:
    """Карта GraphQL TaskStatusGQL на domain TaskStatus"""
    return TaskStatus(status.value)

@strawberry.type
class TaskGQL:
    id: strawberry.ID
    title: str
    description: Optional[str] = None
    status: TaskStatusGQL

def map_to_task_gql(task: Task) -> TaskGQL:
    """Карта базы данных на GraphQL"""
    return TaskGQL(
        id=str(task.id),
        title=task.title,
        description=task.description,
        status=TaskStatusGQL(task.status.value) if task.status else None
    )

@strawberry.type
class TaskPageGQL:
    tasks: List[TaskGQL]
    total: int
    pages_count: int

@strawberry.input
class TaskCreateInputGQL:
    title: str
    description: Optional[str] = None

@strawberry.input
class TaskUpdateInputGQL:
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatusGQL] = None

    def to_update_dict(self) -> dict:
        fields = {
            'title': self.title,
            'description': self.description,
            'status': map_to_task_status(self.status) if self.status is not None else None,
        }
        return {k: v for k, v in fields.items() if v is not None}

