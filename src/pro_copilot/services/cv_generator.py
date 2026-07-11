import logging
from pathlib import Path

from pro_copilot.config import settings
from pro_copilot.services.llm import call_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
你是一位專業的履歷撰寫專家。請根據以下職缺描述（JD）和求職者的技能資料，
產生一份量身打造的繁體中文履歷。

履歷格式要求：
- 使用 Markdown 格式
- 包含以下章節：個人簡介、技術技能、工作經歷、專案成果
- 根據 JD 需求調整技能的呈現順序和重點
- 使用 STAR 格式描述具體貢獻和成果
- 強調與 JD 最相關的經驗
- 全部使用繁體中文
- 專業且精煉的用字
"""


async def generate_cv(jd_path: str | Path) -> str:
    """根據 JD 和技能庫生成量身打造的履歷。

    回傳輸出 CV 檔案的路徑字串。
    """
    jd_path = Path(jd_path)
    jd_content = jd_path.read_text(encoding="utf-8")

    # 讀取所有技能檔案
    skills_dir: Path = settings.vault_dir / "skills"
    skills_content = _read_all_skills(skills_dir)

    user_prompt = (
        "## 職缺描述（JD）\n\n"
        + jd_content
        + "\n\n## 求職者技能資料\n\n"
        + skills_content
    )

    logger.info("正在根據 JD '%s' 生成履歷...", jd_path.name)
    result = await call_llm(SYSTEM_PROMPT, user_prompt)

    # 輸出至 jobs 目錄
    jobs_dir: Path = settings.jobs_dir
    jobs_dir.mkdir(parents=True, exist_ok=True)
    output_filename = f"{jd_path.stem}-CV.md"
    output_path = jobs_dir / output_filename

    output_path.write_text(result, encoding="utf-8")
    logger.info("履歷已生成: %s", output_path)
    return str(output_path)


def _read_all_skills(skills_dir: Path) -> str:
    """讀取 vault/skills/ 下所有技能 Markdown 檔案。"""
    if not skills_dir.exists():
        return "（尚無技能資料）"

    parts: list[str] = []
    for f in sorted(skills_dir.glob("*.md")):
        parts.append(f.read_text(encoding="utf-8"))

    return "\n\n---\n\n".join(parts) if parts else "（尚無技能資料）"
