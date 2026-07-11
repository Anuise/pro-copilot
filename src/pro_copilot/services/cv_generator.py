import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from pro_copilot.config import settings
from pro_copilot.services.llm import call_llm
from pro_copilot.services.vector_service import search_relevant_skills
from pro_copilot.models import CVHistory

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


async def generate_cv(
    jd_content_or_path: str | Path,
    jd_title: str | None = None,
    db: AsyncSession | None = None
) -> str:
    """根據 JD 和技能庫生成量身打造的履歷。

    回傳生成的履歷內容（Markdown 格式）。
    """
    if isinstance(jd_content_or_path, Path) or (isinstance(jd_content_or_path, str) and Path(jd_content_or_path).exists()):
        jd_path = Path(jd_content_or_path)
        jd_content = jd_path.read_text(encoding="utf-8")
        if not jd_title:
            jd_title = jd_path.stem
    else:
        jd_content = str(jd_content_or_path)
        if not jd_title:
            jd_title = "未命名職缺"

    # 使用 Qdrant 檢索最相關的技能
    logger.info("正在透過 Qdrant 檢索與 JD 相關的技能...")
    relevant_skills = await search_relevant_skills(jd_content, limit=5)
    
    if relevant_skills:
        skills_content = "\n\n---\n\n".join(
            [f"### {s['title']}\n\n{s['content']}" for s in relevant_skills]
        )
        logger.info("檢索到 %d 個相關技能。", len(relevant_skills))
    else:
        logger.warning("未檢索到相關技能，回退至讀取全部技能檔案...")
        skills_dir: Path = settings.vault_dir / "skills"
        skills_content = _read_all_skills(skills_dir)

    user_prompt = (
        "## 職缺描述（JD）\n\n"
        + jd_content
        + "\n\n## 求職者技能資料\n\n"
        + skills_content
    )

    logger.info("正在根據 JD '%s' 生成履歷...", jd_title)
    result = await call_llm(SYSTEM_PROMPT, user_prompt)

    # 輸出至 jobs 目錄（保留本地檔案以相容舊有 CLI）
    jobs_dir: Path = settings.jobs_dir
    jobs_dir.mkdir(parents=True, exist_ok=True)
    
    import re
    slug_title = re.sub(r"[^\w\s-]", "", jd_title)
    slug_title = re.sub(r"[\s]+", "_", slug_title.strip()).lower()
    output_filename = f"{slug_title}-CV.md"
    output_path = jobs_dir / output_filename

    output_path.write_text(result, encoding="utf-8")
    logger.info("履歷已同步寫入本地檔案: %s", output_path)

    # 如果有資料庫連線，寫入資料庫
    if db:
        try:
            cv_hist = CVHistory(
                jd_title=jd_title,
                jd_content=jd_content,
                generated_cv=result
            )
            db.add(cv_hist)
            await db.commit()
            logger.info("已將履歷生成歷史寫入 PostgreSQL 中。")
        except Exception as exc:
            logger.error("無法寫入履歷歷史至 PostgreSQL: %s", exc)

    return result


def _read_all_skills(skills_dir: Path) -> str:
    """讀取 vault/skills/ 下所有技能 Markdown 檔案。"""
    if not skills_dir.exists():
        return "（尚無技能資料）"

    parts: list[str] = []
    for f in sorted(skills_dir.glob("*.md")):
        parts.append(f.read_text(encoding="utf-8"))

    return "\n\n---\n\n".join(parts) if parts else "（尚無技能資料）"
