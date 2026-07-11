import asyncio
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pro_copilot.config import settings

logger = logging.getLogger(__name__)


async def sync_weekly_events() -> str:
    """從 Google Calendar 同步過去 7 天的事件，輸出為 Markdown 檔案。

    回傳輸出檔案的路徑字串。
    """
    credentials_path = settings.raw_logs_dir / "calendar" / "credentials.json"
    if not credentials_path.exists():
        logger.warning(
            "Google Calendar 憑證檔案不存在: %s，跳過同步。", credentials_path
        )
        return ""

    events = await asyncio.get_event_loop().run_in_executor(
        None, _fetch_events, credentials_path
    )

    now = datetime.now(timezone.utc)
    iso_week = now.strftime("%G-W%V")
    week_start = now - timedelta(days=7)

    output_dir = settings.raw_logs_dir / "calendar"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{iso_week}.md"

    lines: list[str] = [
        "---",
        f"date_range: {week_start.strftime('%Y-%m-%d')} ~ {now.strftime('%Y-%m-%d')}",
        "source: google_calendar",
        "---",
        "",
        f"# 行事曆事件 {iso_week}",
        "",
    ]

    if not events:
        lines.append("本週無事件。")
    else:
        for event in events:
            start = event.get("start", {}).get(
                "dateTime", event.get("start", {}).get("date", "未知")
            )
            end = event.get("end", {}).get(
                "dateTime", event.get("end", {}).get("date", "")
            )
            summary = event.get("summary", "（無標題）")
            description = event.get("description", "")

            lines.append(f"## {summary}")
            lines.append("")
            lines.append(f"- **日期時間**: {start} ~ {end}")
            if description:
                lines.append(f"- **描述**: {description}")
            lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("行事曆事件已同步至 %s", output_path)
    return str(output_path)


def _fetch_events(credentials_path: Path) -> list[dict]:
    """透過 Google Calendar API 取得過去 7 天的事件（同步呼叫）。"""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials.from_authorized_user_file(str(credentials_path))
    service = build("calendar", "v3", credentials=creds)

    now = datetime.now(timezone.utc)
    time_min = (now - timedelta(days=7)).isoformat()
    time_max = now.isoformat()

    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return result.get("items", [])
