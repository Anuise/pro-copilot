from pathlib import Path

import openai
from pro_copilot.config import settings


async def transcribe(audio_path: str | Path) -> str:
    """使用 OpenAI Whisper 模型將音檔轉錄為文字。"""
    if not settings.openai_api_key or "placeholder" in settings.openai_api_key:
        return "這是一段測試環境語音轉錄的 Mock 文字結果。"
        
    audio_path = Path(audio_path)
    client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
    with open(audio_path, "rb") as audio_file:
        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="zh",
        )
    return transcript.text
