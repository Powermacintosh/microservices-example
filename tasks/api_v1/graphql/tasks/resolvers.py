import strawberry
# from graphql import GraphQLError
from .schemas import (
    TaskGQL,
    TaskPageGQL,
    TaskCreateInputGQL,
    TaskUpdateInputGQL,
    TaskStatusGQL,
    map_to_task_gql
)
from typing import Optional
from core.schemas.tasks import (
    TaskCreate,
    TaskUpdatePartial,
)

@strawberry.type
class Query:
    @strawberry.field
    async def task(
        self,
        id: strawberry.ID,
        info: strawberry.Info,
    ) -> Optional[TaskGQL]: 
        task = await info.context.task_service.get_task(id)
        if task is None:
            return None
        return map_to_task_gql(task)

    @strawberry.field
    async def tasks(
        self,
        status: Optional[TaskStatusGQL] = None,
        offset: int = 0,
        limit: int = 10,
        info: strawberry.Info = strawberry.UNSET,
    ) -> TaskPageGQL:
        task_service = info.context.task_service
        """Получение списка задач с опциональным фильтром по статусу."""
        status_value = status.value if status else None
        
        tasks_data = await task_service.get_tasks(
            page=(offset // limit) + 1,
            limit=limit,
            column_search='status' if status else None,
            input_search=status_value
        )
        
        tasks = [map_to_task_gql(task) for task in tasks_data.tasks]
        
        return TaskPageGQL(
            tasks=tasks,
            total=tasks_data.total,
            pages_count=tasks_data.pages_count
        )

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_task(
        self,
        input: TaskCreateInputGQL,
        info: strawberry.Info,
    ) -> TaskGQL:
        task_data = TaskCreate(
            title=input.title,
            description=input.description
        )
        task = await info.context.task_service.create_task(task_data)
        return map_to_task_gql(task)

    @strawberry.mutation
    async def update_task(
        self,
        id: strawberry.ID,
        input: TaskUpdateInputGQL,
        info: strawberry.Info,
    ) -> Optional[TaskGQL]:
        task = await info.context.task_service.get_task(id)
        if task is None:
            return None
        updated_task = await info.context.task_service.update_task(
            task, TaskUpdatePartial(**input.to_update_dict()), partial=True
        )
        return map_to_task_gql(updated_task) if updated_task else None

    @strawberry.mutation
    async def delete_task(
        self,
        id: strawberry.ID,
        info: strawberry.Info,
    ) -> bool:
        task = await info.context.task_service.get_task(id)
        if task is None:
            return False
        await info.context.task_service.delete_task(task)
        return True




# Автоматический маппинг (если много моделей)
# def input_to_partial(input_obj, mapping: dict = None) -> dict:
#     data = {}
#     for field, value in vars(input_obj).items():
#         if value is not None:
#             if mapping and field in mapping:
#                 data[field] = mapping[field](value)
#             else:
#                 data[field] = value
#     return data

# clean_fields = input_to_partial(
#     input,
#     mapping={"status": map_to_task_status}
# )
# updated_task_data = TaskUpdatePartial(**clean_fields)

