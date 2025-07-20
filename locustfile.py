import random
import time

from locust import FastHttpUser, task


def between(min_val: float, max_val: float) -> float:
    return min_val + random.random() * (max_val - min_val)


class ShortenUser(FastHttpUser):
    @task
    def shorten(self) -> None:
        url = "http://google.com"
        slug = ""
        with self.rest("POST", "/shorten", json={"long_url": url}) as resp:
            if resp.js and "slug" in resp.js:
                slug = resp.js["slug"]
            else:
                resp.failure("Missing slug from response")

        visits = random.randint(0, 15)
        for _ in range(visits):
            time.sleep(between(0.5, 4))
            with self.client.get(f"/{slug}", name="/slug", catch_response=True, allow_redirects=False) as resp:
                if resp.status_code != 307:
                    resp.failure(f"Invalid status code: {resp.status_code}")
