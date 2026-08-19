from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.analytics import router as analytics_router
from app.api.v1.campaigns import router as campaigns_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.discover import router as discover_router
from app.api.v1.health import router as health_router
from app.api.v1.leads import router as leads_router
from app.api.v1.messages import router as messages_router
from app.api.v1.saved_searches import router as saved_searches_router
from app.api.v1.templates import router as templates_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()
settings = get_settings()

app = FastAPI(title="Business Lead Finder API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(discover_router, prefix="/api/v1")
app.include_router(leads_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(templates_router, prefix="/api/v1")
app.include_router(campaigns_router, prefix="/api/v1")
app.include_router(messages_router, prefix="/api/v1")
app.include_router(saved_searches_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
