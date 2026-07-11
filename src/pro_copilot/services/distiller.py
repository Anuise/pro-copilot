import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pro_copilot.config import settings
from pro_copilot.services.llm import call_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
你是一位職涯技能分析專家。請分析以下原始工作記錄，執行以下任務：

1. 過濾雜訊，僅保留與技能、貢獻相關的內容
2. 提取技能與貢獻，使用 STAR 格式（情境、任務、行動、結果）
3. 根據現有技能檔案，判斷需要更新或新增哪些技能頁面
4. 輸出結構化的 Markdown 格式

輸出格式要求：
- 每個技能類別用 ## 標題
- 標記 [更新] 或 [新增] 表示該技能頁面的操作類型
- 每個技能項目包含：技能名稱、熟練度、相關專案、具體貢獻（STAR 格式）
- 全部使用繁體中文
"""


async def run_weekly_distillation() -> None:
    """掃描過去 7 天的原始記錄，透過 LLM 蒸餾為技能更新。"""
    raw_logs_dir: Path = settings.raw_logs_dir
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    new_logs = _collect_recent_logs(raw_logs_dir, cutoff)

    if not new_logs:
        logger.info("過去 7 天沒有新的原始記錄，跳過蒸餾。")
        return

    logger.info("找到 %d 筆新記錄，開始蒸餾...", len(new_logs))

    combined_logs = "\n\n---\n\n".join(new_logs)

    # 讀取現有技能檔案作為上下文
    skills_dir: Path = settings.vault_dir / "skills"
    existing_skills = _read_existing_skills(skills_dir)

    user_prompt = (
        "## 現有技能檔案\n\n"
        + existing_skills
        + "\n\n## 新的原始記錄\n\n"
        + combined_logs
    )

    result = await call_llm(SYSTEM_PROMPT, user_prompt)

    sections = _parse_sections(result)
    created_count = 0
    updated_count = 0

    skills_dir.mkdir(parents=True, exist_ok=True)
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for title, body, is_update in sections:
        filename = _slugify(title) + ".md"
        filepath = skills_dir / filename

        if filepath.exists() and is_update:
            existing = filepath.read_text(encoding="utf-8")
            # 在現有內容後附加新內容
            updated = existing.rstrip() + f"\n\n## 更新 ({now_str})\n\n" + body
            filepath.write_text(updated, encoding="utf-8")
            updated_count += 1
        else:
            frontmatter = "\n".join(
                [
                    "---",
                    f"title: {title}",
                    f"tags: [技能, {title}]",
                    f"created_at: {now_str}",
                    "---",
                    "",
                ]
            )
            filepath.write_text(frontmatter + body, encoding="utf-8")
            created_count += 1

    logger.info(
        "蒸餾完成：新增 %d 個技能檔案，更新 %d 個技能檔案。",
        created_count,
        updated_count,
    )


def _collect_recent_logs(raw_logs_dir: Path, cutoff: datetime) -> list[str]:
    """收集指定目錄下近期修改的記錄檔案。"""
    patterns = ["gitlab/*.json", "calendar/*.md", "voice/*.md"]
    logs: list[str] = []

    for pattern in patterns:
        for filepath in raw_logs_dir.glob(pattern):
            mtime = datetime.fromtimestamp(
                filepath.stat().st_mtime, tz=timezone.utc
            )
            if mtime >= cutoff:
                content = filepath.read_text(encoding="utf-8")
                # JSON 檔案轉為可讀格式
                if filepath.suffix == ".json":
                    try:
                        data = json.loads(content)
                        content = json.dumps(
                            data, ensure_ascii=False, indent=2
                        )
                    except json.JSONDecodeError:
                        pass
                logs.append(f"### 來源: {filepath.name}\n\n{content}")

    return logs


def _read_existing_skills(skills_dir: Path) -> str:
    """讀取現有技能檔案的內容。"""
    if not skills_dir.exists():
        return "（尚無現有技能檔案）"

    parts: list[str] = []
    for f in sorted(skills_dir.glob("*.md")):
        parts.append(f"### {f.stem}\n\n{f.read_text(encoding='utf-8')}")

    return "\n\n".join(parts) if parts else "（尚無現有技能檔案）"


def _parse_sections(text: str) -> list[tuple[str, str, bool]]:
    """將 LLM 輸出按 ## 標題分割為 (標題, 內容, 是否更新) 清單。"""
    sections: list[tuple[str, str, bool]] = []
    current_title = ""
    current_lines: list[str] = []
    is_update = False

    for line in text.splitlines():
        if line.startswith("## "):
            if current_title:
                sections.append(
                    (current_title, "\n".join(current_lines), is_update)
                )
            raw_title = line[3:].strip()
            is_update = "[更新]" in raw_title
            current_title = (
                raw_title.replace("[更新]", "").replace("[新增]", "").strip()
            )
            current_lines = []
        else:
            current_lines.append(line)

    if current_title:
        sections.append((current_title, "\n".join(current_lines), is_update))

    return sections


def _slugify(text: str) -> str:
    """將標題轉為適合檔名的格式。"""
    import re

    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s]+", "_", text.strip())
    return text.lower() or "untitled"
