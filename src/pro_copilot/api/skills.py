import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException

from pro_copilot.config import settings
from pro_copilot.services.vector_service import sync_skills_to_vector_db

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def list_skills():
    """列出 vault/skills 下所有技能 Markdown 卡片。"""
    skills_dir: Path = settings.vault_dir / "skills"
    if not skills_dir.exists():
        return []
    
    skills = []
    for filepath in sorted(skills_dir.glob("*.md")):
        if filepath.name == ".gitkeep":
            continue
        try:
            content = filepath.read_text(encoding="utf-8")
            # 取得簡短摘要
            summary = ""
            for line in content.splitlines():
                if line.strip() and not line.startswith("---") and not line.startswith("title:") and not line.startswith("tags:"):
                    summary = line.strip()[:100]
                    if len(line.strip()) > 100:
                        summary += "..."
                    break
            
            skills.append({
                "filename": filepath.name,
                "title": filepath.stem,
                "summary": summary,
                "content": content
            })
        except Exception as exc:
            logger.error("讀取技能卡片失敗 %s: %s", filepath.name, exc)
            
    return skills

@router.post("/sync-vector")
async def sync_vector():
    """將技能 Wiki 的所有 Markdown 卡片同步到 Qdrant。"""
    try:
        count = await sync_skills_to_vector_db()
        return {"status": "success", "synced_count": count}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"向量資料庫同步失敗: {exc}")

@router.get("/logs")
async def get_activity_logs():
    """掃描 raw_logs 底下的檔案，提供近期系統同步活動的清單。"""
    import os
    from datetime import datetime
    
    raw_dir: Path = settings.raw_logs_dir
    logs = []
    
    categories = {
        "gitlab": "GitLab Webhook 事件",
        "calendar": "行事曆同步",
        "voice": "語音筆記轉錄"
    }
    
    for folder, desc in categories.items():
        folder_path = raw_dir / folder
        if folder_path.exists():
            for f in folder_path.glob("*"):
                if f.name == ".gitkeep":
                    continue
                stat = f.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                logs.append({
                    "name": f.name,
                    "category": folder,
                    "description": desc,
                    "size": stat.st_size,
                    "time": mtime
                })
                
    # 排序：越新越前面
    logs.sort(key=lambda x: x["time"], reverse=True)
    return logs[:20]
