
class TaskNotFoundException(Exception):
    """Исключение для задачи, которая не найдена"""
    def __init__(self, task_id: str):
        super().__init__(
            f'Задача {task_id} не найдена!'
        )