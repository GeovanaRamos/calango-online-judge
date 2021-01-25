import json

from locust import HttpLocust, TaskSet, task, HttpUser, between


class UserActions(HttpUser):
    wait_time = between(3, 5)

    # def on_start(self):
    #     self.login()
    #
    # def login(self):
    #     # login to the application
    #     response = self.client.get('/accounts/login/')
    #     csrftoken = response.cookies['csrftoken']
    #     self.client.post('/accounts/login/',
    #                      {'username': 'aluno@email.com', 'password': 'admin'},
    #                      headers={'X-CSRFToken': csrftoken})
    #
    # @task(1)
    # def submit_code(self):
    #     for _ in range(50):
    #         response = self.client.get('/schedules/1/questions/2/submissions/create/')
    #         csrftoken = response.cookies['csrftoken']
    #         self.client.post('/schedules/1/questions/2/submissions/create/', {
    #             'code': "algoritmo teste;\n\nprincipal\n\n\nenquanto(0==0) faca\nfimEnquanto\n\nfimPrincipal"},
    #                      headers={'X-CSRFToken': csrftoken})

    # @task
    # def submit_code(self):
    #     self.client.post('/judge',
    #                      json.dumps({
    #                                     'code': "algoritmo teste;\n\nprincipal\n\n\n\n\n\nfimPrincipal",
    #                                     'cases': [{'input': ['a', 'b'], 'output': 'a'}]}),
    #                      headers={'content-type': 'application/json'})
