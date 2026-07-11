from contextlib import asynccontextmanager

from fastapi import FastAPI

from pro_copilot.api.calendar import router as calendar_router
from pro_copilot.api.gitlab import router as gitlab_router
from pro_copilot.api.voice import router as voice_router
from pro_copilot.config import settings
from pro_copilot.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理：建立資料目錄、啟動排程器。"""
    data_dirs = [
        settings.raw_logs_dir / "gitlab",
        settings.raw_logs_dir / "calendar",
        settings.raw_logs_dir / "voice",
        settings.vault_dir / "skills",
        settings.vault_dir / "daily",
        settings.jobs_dir,
    ]
    for d in data_dirs:
        d.mkdir(parents=True, exist_ok=True)

    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Pro-Copilot",
    version="1.0.0",
    description="個人職涯副駕駛 — 整合語音筆記、GitLab 事件、行事曆同步與每週蒸餾的智慧助手。",
    lifespan=lifespan,
)

app.include_router(gitlab_router, prefix="/api/gitlab", tags=["GitLab"])
app.include_router(voice_router, prefix="/api/voice", tags=["Voice"])
app.include_router(calendar_router, prefix="/api/calendar", tags=["Calendar"])


@app.get("/health")
async def health():
    """健康檢查端點。"""
    return {"status": "ok"}
