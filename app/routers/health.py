from fastapi import APIRouter
from sqlalchemy import text

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
