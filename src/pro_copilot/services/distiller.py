import json
import logging
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from pro_copilot.config import settings
from pro_copilot.services.document_converter import run_document_conversion
from pro_copilot.services.llm import call_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
你是一位職涯技能分析專家。請分析以下原始工作記錄，執行以下任務：

1. 過濾雜訊，僅保留與技能、貢獻相關的內容
2. 提取技能與貢獻，使用 STAR 格式（情境、任務、行動、結果）
3. 根據現有技能檔案，判斷需要更新或新增哪些技能頁面
4. 輸出結構化的 Markdown 格式，並且不要包含任何 YAML frontmatter (程式會自動處理)

對於每一個技能項目，你必須嚴格遵守以下輸出格式模板：

## [操作類型] 技能名稱
（操作類型為 [新增] 或 [更新]）

## 技能說明
- **核心描述**：[簡述此技能的專業定義與主要應用場景]
- **熟練程度**：[精通 / 熟練 / 熟悉 / 基礎]
- **核心技術**：[技術 A, 技術 B, 技術 C]

## 實際專案紀錄

### [專案名稱]
- **情境 (Situation)**：[情境說明]
- **任務 (Task)**：[任務說明]
- **行動 (Action)**：[行動說明]
- **結果 (Result)**：[結果說明]

規範限制：
- 如果該技能是 [更新]，你必須閱讀「現有技能檔案」中對應的內容，將既有的歷史專案紀錄完整保留，並將新專案以相同的 STAR 格式追加在「## 實際專案紀錄」底下。你可以根據新的工作表現，重新調整「## 技能說明」中的核心描述、熟練程度與核心技術標籤。
- 全部使用繁體中文。
"""


def _extract_frontmatter(content: str) -> str:
    """從 Markdown 內容中提取 YAML frontmatter。如果沒有則回傳空字串。"""
    if not content.startswith("---"):
        return ""
    lines = content.splitlines(keepends=True)
    if not lines or not lines[0].startswith("---"):
        return ""
    
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].startswith("---"):
            end_idx = i
            break
            
    if end_idx != -1:
        return "".join(lines[:end_idx + 1])
    return ""


async def run_weekly_distillation() -> None:
    """掃描過去 7 天的原始記錄，透過 LLM 蒸餾為技能更新。"""
    # 先執行文件格式轉換
    try:
        await run_document_conversion()
    except Exception as exc:
        logger.error("自動執行文件轉換失敗: %s", exc, exc_info=True)

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
            frontmatter = _extract_frontmatter(existing)
            if not frontmatter:
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
            # 直接用原來的 frontmatter 加上 LLM 輸出的最新完整 body (body 開頭是 ## 技能說明...)
            filepath.write_text(frontmatter + body, encoding="utf-8")
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
    patterns = ["gitlab/*.json", "calendar/*.md", "voice/*.md", "documents/*.md"]
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
        if line.startswith("## ") and ("[新增]" in line or "[更新]" in line):
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
