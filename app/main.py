from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.routers import (
    audit_logs,
    auth,
    health,
    inventory,
    invoices,
    orders,
    purchase_orders,
    suppliers,
    warehouses,
)
from app.utils.audit import register_audit_listeners

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    register_audit_listeners()
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        description=(
            "Standalone ERP backend for KIT Kolhapur (CSBS) mini-project. "
            "Designed for integration with SynChain AI over REST. "
            "Authenticate with `X-API-Key` (service-to-service) or JWT Bearer token."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    prefix = settings.API_V1_PREFIX
    application.include_router(health.router, prefix=prefix)
    application.include_router(auth.router, prefix=prefix)
    application.include_router(suppliers.router, prefix=prefix)
    application.include_router(warehouses.router, prefix=prefix)
    application.include_router(inventory.router, prefix=prefix)
    application.include_router(purchase_orders.router, prefix=prefix)
    application.include_router(orders.router, prefix=prefix)
    application.include_router(invoices.router, prefix=prefix)
    application.include_router(audit_logs.router, prefix=prefix)

    @application.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status_code": exc.status_code,
                "message": exc.message,
                "detail": exc.error_detail,
            },
        )

    @application.exception_handler(RequestValidationError)
    async def validation_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status_code": 422,
                "message": "Validation error",
                "detail": jsonable_encoder(exc.errors()),
            },
        )

    @application.exception_handler(SQLAlchemyError)
    async def sqlalchemy_handler(_request: Request, exc: SQLAlchemyError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": 500,
                "message": "A database error occurred",
                "detail": str(exc.__class__.__name__),
            },
        )

    def custom_openapi():
        if application.openapi_schema:
            return application.openapi_schema
        openapi_schema = get_openapi(
            title=application.title,
            version=application.version,
            description=application.description,
            routes=application.routes,
        )
        openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})
        openapi_schema["components"]["securitySchemes"].update(
            {
                "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
                "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
            }
        )
        openapi_schema["security"] = [{"ApiKeyAuth": []}, {"BearerAuth": []}]
        application.openapi_schema = openapi_schema
        return application.openapi_schema

    application.openapi = custom_openapi
    return application


app = create_app()
