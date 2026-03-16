import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routers import chat, digests, health, internal_jobs, search, signals, users
from app.core import configure_logging, get_app_config
from app.ingestion.workers.pipeline import run_crawler
from app.ingestion.scheduler import build_scheduler

configure_logging(level=logging.INFO)
logger = logging.getLogger(__name__)
config = get_app_config()

scheduler = build_scheduler(config)

@asynccontextmanager
async def lifespan(_: FastAPI):
    await run_crawler()  # chạy 1 lần ngay lúc start
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)

app = FastAPI(lifespan=lifespan)
app.include_router(health.router)
app.include_router(signals.router)
app.include_router(chat.router)
app.include_router(search.router)
app.include_router(users.router)
app.include_router(digests.router)
app.include_router(internal_jobs.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and exc.detail.get("code") and exc.detail.get("message"):
        return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "HTTP_ERROR", "message": str(exc.detail)}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters.",
                "details": {"items": exc.errors()},
            }
        },
    )