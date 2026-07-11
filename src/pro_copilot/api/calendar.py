from fastapi import APIRouter, HTTPException

from pro_copilot.services.calendar_sync import sync_weekly_events

router = APIRouter()


@router.post("/sync")
async def sync_calendar():
    """同步本週 Google Calendar 事件。"""
    try:
        output_path = await sync_weekly_events()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"行事曆同步失敗: {exc}")

    return {"status": "synced", "file": str(output_path)}
