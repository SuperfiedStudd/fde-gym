import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from redis.asyncio import Redis

from app.config import get_settings
from app.logging import configure_logging
from app.metrics import HTTP_DURATION, HTTP_REQUESTS
from app.mission_store import MissionStore
from app.progress_store import ProgressStore
from app.routes import claims, events, missions, system

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis.from_url(settings.redis_url, decode_responses=True)
    app.state.missions = MissionStore(settings.mission_root)
    app.state.progress = ProgressStore(settings.progress_file)
    yield
    await app.state.redis.aclose()


app = FastAPI(
    title="ClaimOps API",
    version="0.1.0",
    description="The deliberately imperfect backend for fde-gym.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(missions.router)
app.include_router(claims.router)
app.include_router(events.router)
app.include_router(system.router)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    started = time.perf_counter()
    response = await call_next(request)
    route = request.scope.get("route")
    route_path = getattr(route, "path", request.url.path)
    elapsed = time.perf_counter() - started
    HTTP_REQUESTS.labels(request.method, route_path, response.status_code).inc()
    HTTP_DURATION.labels(request.method, route_path).observe(elapsed)
    response.headers["x-request-id"] = request_id
    logger.info(
        "request_complete",
        extra={
            "request_id": request_id,
            "method": request.method,
            "route": route_path,
            "status": response.status_code,
            "duration_ms": round(elapsed * 1000, 2),
        },
    )
    return response


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "environment": settings.environment}


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
