from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.db.session import engine
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, openapi_extra={"security": []})
def health_check() -> HealthResponse:
    settings = get_settings()
    db_status = "connected"
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        db_status = "unavailable"
    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        service=settings.APP_NAME,
        database=db_status,
    )


@router.get("/health/ready", tags=["Health"], response_model=HealthResponse, openapi_extra={"security": []})
def health_ready() -> HealthResponse:
    """Same as /health but reachable at a distinct path for readiness probes.

    Kept separate from /api/v1/health so load balancers and orchestrators can hit
    a single known path without needing the API version prefix or auth.
    """
    settings = get_settings()
    db_status = "connected"
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        db_status = "unavailable"
    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        service=settings.APP_NAME,
        database=db_status,
    )
