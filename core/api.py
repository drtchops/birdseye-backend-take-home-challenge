import sentry_sdk
from fastapi import FastAPI

from core.config import get_settings
from shortlinks.routes import router as shortlinks_router
from stats.routes import router as stats_router

settings = get_settings()

if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn, send_default_pii=False)

app = FastAPI()

app.include_router(stats_router)
app.include_router(shortlinks_router)
