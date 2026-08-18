from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.discover import router as discover_router
from app.api.v1.health import router as health_router
from app.api.v1.leads import router as leads_router
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
