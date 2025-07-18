from fastapi import FastAPI

from shortlinks.routes import router as shortlinks_router

app = FastAPI()
app.include_router(shortlinks_router)
