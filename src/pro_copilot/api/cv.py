from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pro_copilot.database import get_db
from pro_copilot.models import CVHistory
from pro_copilot.services.cv_generator import generate_cv

router = APIRouter()

class CVGenerateRequest(BaseModel):
    jd_content: str
    jd_title: str | None = None

@router.post("/generate")
async def api_generate_cv(req: CVGenerateRequest, db: AsyncSession = Depends(get_db)):
    """針對傳入的 Job Description (JD) 生成客製化履歷，並寫入資料庫歷史紀錄。"""
    try:
        cv_text = await generate_cv(
            jd_content_or_path=req.jd_content,
            jd_title=req.jd_title,
            db=db
        )
        return {"status": "success", "cv": cv_text}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"履歷生成失敗: {exc}")

@router.get("/history")
async def get_cv_history(db: AsyncSession = Depends(get_db)):
    """取得 PostgreSQL 中的履歷生成歷史紀錄。"""
    try:
        stmt = select(CVHistory).order_by(CVHistory.created_at.desc())
        result = await db.execute(stmt)
        histories = result.scalars().all()
        return [
            {
                "id": h.id,
                "jd_title": h.jd_title,
                "jd_content": h.jd_content,
                "generated_cv": h.generated_cv,
                "created_at": h.created_at
            }
            for h in histories
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"讀取履歷歷史失敗: {exc}")
