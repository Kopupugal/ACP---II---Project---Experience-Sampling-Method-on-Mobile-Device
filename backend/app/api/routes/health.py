from datetime import UTC, datetime

from fastapi import APIRouter

from backend.app.schemas.common import HealthResponse


router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return a lightweight readiness response."""
    return HealthResponse(status="ok", service="esm-platform-api", timestamp=datetime.now(UTC))
