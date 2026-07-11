import logging
from datetime import datetime, timezone
from pathlib import Path

from pro_copilot.config import settings
from pro_copilot.services.llm import call_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
你是一位職涯分析專家。請分析以下歷史履歷資料，提取所有技能、技術、專案經驗，
並按類別整理成結構化的技能 Wiki 頁面。

輸出格式要求：
- 使用 Markdown 格式
- 每個技能類別用 ## 標題
- 每個技能項目包含：技能名稱、熟練度、相關專案、具體貢獻（STAR 格式）
- 全部使用繁體中文
"""


async def run_bootstrap() -> None:
    """讀取 init 目錄下的履歷資料，透過 LLM 生成技能 Wiki 頁面。"""
    init_dir: Path = settings.init_dir
    md_files = sorted(init_dir.glob("*.md"))

    if not md_files:
        logger.warning("init 目錄中沒有找到 .md 檔案: %s", init_dir)
        return

    print("📂 正在讀取履歷資料...")
    contents: list[str] = []
    for f in md_files:
        print(f"  讀取: {f.name}")
        contents.append(f.read_text(encoding="utf-8"))

    combined = "\n\n---\n\n".join(contents)

    print("🤖 正在呼叫 LLM 分析技能...")
    result = await call_llm(SYSTEM_PROMPT, combined)

    skills_dir: Path = settings.vault_dir / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    sections = _parse_sections(result)
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for title, body in sections:
        filename = _slugify(title) + ".md"
        filepath = skills_dir / filename

        frontmatter = "\n".join(
            [
                "---",
                f"title: {title}",
                f"tags: [技能, {title}]",
                f"created_at: {created_at}",
                "---",
                "",
            ]
        )
        filepath.write_text(frontmatter + body, encoding="utf-8")
        print(f"  ✅ 已建立: {filepath.name}")

    print(f"🎉 技能 Wiki 建立完成，共 {len(sections)} 個類別。")


def _parse_sections(text: str) -> list[tuple[str, str]]:
    """將 LLM 輸出按 ## 標題分割為 (標題, 內容) 清單。"""
    sections: list[tuple[str, str]] = []
    current_title = ""
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_title:
                sections.append((current_title, "\n".join(current_lines)))
            current_title = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_title:
        sections.append((current_title, "\n".join(current_lines)))

    return sections


def _slugify(text: str) -> str:
    """將標題轉為適合檔名的格式。"""
    import re

    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s]+", "_", text.strip())
    return text.lower() or "untitled"
