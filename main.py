from contextlib import asynccontextmanager
from typing import AsyncGenerator, Awaitable, Callable
from fastapi import FastAPI
from src.api import customers_router, orders_router, payments_router
from src.core.logger import setup_logging, get_logger

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
import time
import uvicorn
from src.core.config import settings


setup_logging(settings.LOG_LEVEL)
logger = get_logger("main")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="REST API for work with CRM",
    version=settings.VERSION,
    openapi_url=f"{settings.API_VERSION_STR}/openapi.json",
    docs_url=f"{settings.API_VERSION_STR}/docs",
    redoc_url=f"{settings.API_VERSION_STR}/redoc",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan event handler для управления жизненным циклом приложения.
    Заменяет устаревшие on_event("startup") и on_event("shutdown").
    """
    # Startup
    logger.info("CRM CRUD API starting up")
    yield
    # Shutdown
    logger.info("CRM CRUD API shutting down")


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    """Middleware for logging HTTP requests and responses"""
    start_time = time.time()
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client": request.client.host if request.client else None,
        },
    )
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": f"{process_time:.3f}s",
            },
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Error processing request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
                "process_time": f"{process_time:.3f}s",
            },
            exc_info=True,
        )
        raise


app.include_router(customers_router, prefix=settings.API_VERSION_STR)
app.include_router(orders_router, prefix=settings.API_VERSION_STR)
app.include_router(payments_router, prefix=settings.API_VERSION_STR)


@app.get("/")
async def root():
    """Root endpoint with info about the API."""
    logger.debug("Root endpoint accessed")
    return {
        "message": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": f"{settings.API_VERSION_STR}/docs",
        "endpoints": {
            "customers": "/customers",
            "orders": "/orders",
            "payments": "/payments",
        },
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
