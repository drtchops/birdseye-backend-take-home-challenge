from fastapi import FastAPI

from shortlinks.routes import router as shortlinks_router
from stats.routes import router as stats_router

app = FastAPI()
app.include_router(stats_router)
app.include_router(shortlinks_router)
