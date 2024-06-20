from locust import HttpUser, between, task


class QuickstartUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def create_post(self):
        # file for image
        image = open("./assets/test.jpg", "rb")
        self.client.post("/api/books", files={"image": image}, data={
            "title": "Sample Title",
            "description": "Sample Description"
        })
