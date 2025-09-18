from locust import FastHttpUser, task, between
# from core.config import settings

class UserBehavior(FastHttpUser):
    wait_time = between(1, 2)

    @task
    def create_task_event(self):
        self.client.post('/api/v1/task/create_event', json={
            'title': 'Create Task',
            'description': None,
        })
