from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pro_copilot.api.calendar import router as calendar_router
from pro_copilot.api.gitlab import router as gitlab_router
from pro_copilot.api.voice import router as voice_router
from pro_copilot.api.skills import router as skills_router
from pro_copilot.api.cv import router as cv_router
from pro_copilot.api.linkedin import router as linkedin_router
from pro_copilot.config import settings
from pro_copilot.scheduler import start_scheduler, stop_scheduler
from pro_copilot.database import init_db
from pro_copilot.services.vector_service import init_qdrant_collection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理：建立資料目錄、初始化資料庫、啟動排程器。"""
    data_dirs = [
        settings.raw_logs_dir / "gitlab",
        settings.raw_logs_dir / "calendar",
        settings.raw_logs_dir / "voice",
        settings.raw_logs_dir / "incoming",
        settings.raw_logs_dir / "incoming" / "archive",
        settings.raw_logs_dir / "documents",
        settings.vault_dir / "skills",
        settings.vault_dir / "daily",
        settings.jobs_dir,
    ]
    for d in data_dirs:
        d.mkdir(parents=True, exist_ok=True)

    # 初始化資料庫 Table 與 Qdrant 向量集合
    try:
        await init_db()
    except Exception as exc:
        print(f"PostgreSQL 初始化失敗: {exc}")

    try:
        await init_qdrant_collection()
    except Exception as exc:
        print(f"Qdrant 初始化失敗: {exc}")

    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Pro-Copilot",
    version="1.0.0",
    description="個人職涯副駕駛 — 整合語音筆記、GitLab 事件、行事曆同步與每週蒸餾的智慧助手。",
    lifespan=lifespan,
)

# 啟用 CORS 以支援 Next.js 跨域存取
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gitlab_router, prefix="/api/gitlab", tags=["GitLab"])
app.include_router(voice_router, prefix="/api/voice", tags=["Voice"])
app.include_router(calendar_router, prefix="/api/calendar", tags=["Calendar"])
app.include_router(skills_router, prefix="/api/skills", tags=["Skills"])
app.include_router(cv_router, prefix="/api/cv", tags=["CV"])
app.include_router(linkedin_router, prefix="/api/linkedin", tags=["LinkedIn"])


@app.get("/health")
async def health():
    """健康檢查端點。"""
    return {"status": "ok"}
