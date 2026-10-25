from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.studies import router as studies_router
from backend.app.db import models  # noqa: F401
from backend.app.db.session import Base, engine



@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create local tables; production deployments should run Alembic migrations."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="ESM Platform API",
    version="0.1.0",
    description="Foundational study configuration API for the ESM platform.",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(studies_router, prefix="/api/v1")

web_directory = Path(__file__).resolve().parents[2] / "web"
app.mount("/", StaticFiles(directory=web_directory, html=True), name="web")
