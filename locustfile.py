import time

from locust import FastHttpUser, task


class ShortenUser(FastHttpUser):
    @task
    def shorten(self) -> None:
        url = "http://google.com"
        slug = ""
        with self.rest("POST", "/shorten", json={"long_url": url}) as resp:
            if resp.js and "slug" in resp.js:
                slug = resp.js["slug"]
        for _ in range(3):
            time.sleep(1)
            with self.client.get(f"/{slug}", name="/slug", catch_response=True, allow_redirects=False) as resp:
                if resp.status_code != 307:
                    resp.failure(f"Invalid status code: {resp.status_code}")
