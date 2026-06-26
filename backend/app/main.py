import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging_config import configure_logging, get_logger, log_event
from app.controllers import (
    analytics_controller, auth_controller, data_controller,
    job_controller, ml_controller,
)
from app.db.session import init_models

configure_logging()
logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models()
    log_event(logger, logging.INFO, "startup_complete", app=settings.APP_NAME)
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    log_event(
        logger, logging.INFO, "http_request",
        method=request.method, path=request.url.path,
        status_code=response.status_code, response_time_ms=elapsed_ms,
        user_id=getattr(request.state, "user_id", None),
    )
    return response


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}


for r in (auth_controller.router, data_controller.router, analytics_controller.router,
          ml_controller.router, job_controller.router):
    app.include_router(r, prefix=settings.API_PREFIX)
