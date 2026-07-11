import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request

from pro_copilot.config import settings

router = APIRouter()


@router.post("/")
async def receive_gitlab_webhook(request: Request):
    """接收 GitLab Webhook 事件並儲存原始 JSON。"""
    # 驗證 token（若有設定）
    if settings.gitlab_webhook_secret:
        token = request.headers.get("X-Gitlab-Token", "")
        if token != settings.gitlab_webhook_secret:
            raise HTTPException(status_code= 403, detail="Webhook token 驗證失敗")

    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"無法解析 JSON: {exc}")

    project_name = (
        payload.get("project", {}).get("name", "unknown").replace(" ", "_")
    )
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = settings.raw_logs_dir / "gitlab" / f"{timestamp}_{project_name}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return {"status": "received"}
