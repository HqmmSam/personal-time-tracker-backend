import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.handlers import register_exception_handlers
from app.routers import (
    auth,
    users,
    projects,
    tasks,
    records,
    stats,
    predictions,
    settings as settings_router,
)


logging.basicConfig(
    level=logging.DEBUG if settings.app_debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("ptt")


app = FastAPI(title="Personal Time Tracker API", version="1.0.0")


# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- 请求日志 ----------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    logger.info(
        "%s %s -> %s (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# ---------- 异常处理 ----------
register_exception_handlers(app)


# ---------- 健康检查 ----------
@app.get("/health", tags=["健康检查"])
def health():
    return {"status": "ok", "env": settings.app_env}


# ---------- 路由挂载 ----------
API_V1 = "/api/v1"
app.include_router(auth.router, prefix=API_V1)
app.include_router(users.router, prefix=API_V1)
app.include_router(projects.router, prefix=API_V1)
app.include_router(tasks.nested_router, prefix=API_V1)
app.include_router(tasks.flat_router, prefix=API_V1)
app.include_router(records.router, prefix=API_V1)
app.include_router(stats.router, prefix=API_V1)
app.include_router(predictions.router, prefix=API_V1)
app.include_router(settings_router.router, prefix=API_V1)
