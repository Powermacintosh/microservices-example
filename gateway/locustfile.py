from locust import FastHttpUser, task, between
# from core.config import settings

class UserBehavior(FastHttpUser):
    wait_time = between(1, 2)

    @task(1)
    def create_task_event(self):
        self.client.post('/api/v1/task/create_event', json={
            'title': 'Create Task',
            'description': None,
        })
    
    @task(2)
    def create_task(self):
        self.client.post('/api/v1/task/create', json={
            'title': 'Create Task',
            'description': None,
        })

    @task(3)
    def get_tasks_list(self):
        self.client.get('/api/v1/tasks/')

# class CreateTaskOnlyUser(FastHttpUser):
#     wait_time = between(1, 2)

#     @task
#     def create_task(self):
#         self.client.post('/api/v1/task/create', json={
#             'title': 'Create Task',
#             'description': None,
#         })

# class ReadOnlyUser(FastHttpUser):
#     wait_time = between(1, 2)

#     @task
#     def get_tasks(self):
#         self.client.get('/api/v1/tasks/')

# class CreateTaskEventUser(FastHttpUser):
#     wait_time = between(1, 2)

#     @task
#     def create_task_event(self):
#         self.client.post('/api/v1/task/create_event', json={
#             'title': 'Create Task',
#             'description': None,
#         })