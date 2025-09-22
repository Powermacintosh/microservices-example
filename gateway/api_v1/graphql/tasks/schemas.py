import strawberry
from enum import Enum
from typing import Optional, List


@strawberry.enum
class TaskStatusGQL(str, Enum):
    CREATED = 'created'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'

@strawberry.type
class TaskGQL:
    id: strawberry.ID
    title: str
    description: Optional[str] = None
    status: TaskStatusGQL

def map_json_to_task_gql(data: dict) -> TaskGQL:
    """Карта базы данных на GraphQL"""
    return TaskGQL(
        id=data['id'],
        title=data['title'],
        description=data.get('description'),
        status=TaskStatusGQL(data['status'].lower()),
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

    def to_dict(self) -> dict:
        """
        Сериализация в словарь, убирая поля со значениями None.
        Значения enum приводятся к верхнему регистру для GraphQL.
        """
        fields = {
            'title': self.title,
            'description': self.description,
            'status': self.status.value.upper() if self.status is not None else None,
        }
        return {k: v for k, v in fields.items() if v is not None}

