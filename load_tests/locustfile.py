from locust import HttpUser, between, task


class SyncloneUser(HttpUser):
    # Часова затримка між запитами одного користувача (від 1 до 3 секунд)
    wait_time = between(1, 3)

    @task(3)
    def index_page(self):
        """Тестування головної сторінки або базового ендпоінту API"""
        self.client.get("/")

    @task(1)
    def api_docs(self):
        """Тестування доступності документації Swagger (ендпоінт FastAPI)"""
        self.client.get("/docs")
