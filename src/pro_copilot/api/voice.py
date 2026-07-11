from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile

from pro_copilot.config import settings
from pro_copilot.services.whisper import transcribe

router = APIRouter()


@router.post("/")
async def upload_voice_memo(audio: UploadFile):
    """接收語音檔案，轉錄為繁體中文文字。"""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    voice_dir = settings.raw_logs_dir / "voice"
    voice_dir.mkdir(parents=True, exist_ok=True)

    # 儲存音檔
    audio_path = voice_dir / f"{timestamp}.ogg"
    try:
        content = await audio.read()
        with open(audio_path, "wb") as f:
            f.write(content)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"儲存音檔失敗: {exc}")

    # 轉錄
    try:
        transcription = await transcribe(audio_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"語音轉錄失敗: {exc}")

    # 儲存轉錄結果（含 YAML frontmatter）
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    md_path = voice_dir / f"{timestamp}.md"
    md_content = (
        f"---\n"
        f"date: {date_str}\n"
        f"source: voice\n"
        f"---\n\n"
        f"{transcription}\n"
    )
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return {"status": "transcribed", "text": transcription}
