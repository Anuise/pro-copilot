import json
import logging
import re
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from pro_copilot.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic 數據模型
class Experience(BaseModel):
    company: str
    title: str
    location: Optional[str] = ""
    start_date: str
    end_date: str
    description: str

class Education(BaseModel):
    school: str
    degree: str
    start_date: str
    end_date: str

class LinkedInProfile(BaseModel):
    name: str
    headline: str
    location: str
    about: str
    experiences: List[Experience]
    educations: List[Education]

class SkillItem(BaseModel):
    name: str
    proficiency: str
    core_tech: str
    description: str

class LinkedInProfileResponse(BaseModel):
    name: str
    headline: str
    location: str
    about: str
    experiences: List[Experience]
    educations: List[Education]
    skills: List[SkillItem]

DEFAULT_PROFILE = {
    "name": "杜偉宏",
    "headline": "軟體工程師 | 專注於 Python, FastAPI, Next.js 與 AI 應用開發",
    "location": "台灣",
    "about": "熱愛解決問題的軟體工程師，擅長建構高效的後端 API 系統與現代化前端界面。具備大型語言模型 (LLM) 與向量資料庫 (Qdrant) 整合的 RAG 系統開發經驗。",
    "experiences": [
      {
        "company": "某科技公司",
        "title": "軟體工程師",
        "location": "",
        "start_date": "2024-01",
        "end_date": "至今",
        "description": "• 負責設計與開發基於 FastAPI 的後端 API，提供即時資料串流與 WebSocket 通訊，顯著提升通訊效能。\n• 整合大型語言模型與向量資料庫 Qdrant，完成檢索增強生成 (RAG) 系統，提升問答準確率達 15%。\n• 使用 Next.js 與 React 重新設計前端介面，提升載入速度達 40%。\n• 使用 Docker 容器化技術，並建置 Docker Compose 環境，簡化多服務部署流程。"
      }
    ],
    "educations": []
}

def parse_resume_markdown(content: str) -> dict:
    """從個人履歷 Markdown 中解析出 LinkedIn 個人檔案的初始值。"""
    profile = {
        "name": "杜偉宏",
        "headline": "軟體工程師 | 專注於 Python, FastAPI, Next.js 與 AI 應用開發",
        "location": "台灣",
        "about": "熱愛解決問題的軟體工程師，擅長建構高效的後端 API 系統與現代化前端界面。具備大型語言模型 (LLM) 與向量資料庫 (Qdrant) 整合的 RAG 系統開發經驗。",
        "experiences": [],
        "educations": []
    }
    
    # 提取姓名
    first_line_match = re.search(r"^#\s*(.+)$", content, re.MULTILINE)
    if first_line_match:
        raw_line = first_line_match.group(1).strip()
        if " - " in raw_line:
            raw_name = raw_line.split(" - ")[0].strip()
        else:
            raw_name = raw_line
        # 去除括號，例如 "(Wei-Hung Tu)"
        clean_name = re.sub(r"\s*\(.*?\)", "", raw_name).strip()
        if clean_name:
            profile["name"] = clean_name

    # 提取專業技能
    skills = []
    skills_section = re.search(r"##\s*專業技能\n(.*?)(?=\n##|$)", content, re.DOTALL)
    if skills_section:
        for line in skills_section.group(1).splitlines():
            line_str = line.strip()
            if line_str.startswith("-") or line_str.startswith("*"):
                skill_val = re.sub(r"^[-*]\s*", "", line_str).strip()
                if skill_val:
                    skills.append(skill_val)

    # 提取經歷
    exp_blocks = re.finditer(r"###\s*([^|\n]+)\s*\|\s*([^(\n]+)\s*\(([^)\n]+)\)\n(.*?)(?=\n###|\n##|$)", content, re.DOTALL)
    experiences = []
    for match in exp_blocks:
        title = match.group(1).strip()
        company = match.group(2).strip()
        time_period = match.group(3).strip()
        desc_block = match.group(4).strip()

        # 解析時間段
        start_date = "2024-01"
        end_date = "至今"
        if "-" in time_period:
            parts = time_period.split("-")
            start_date_part = parts[0].strip()
            if len(start_date_part) == 4:
                start_date = f"{start_date_part}-01"
            else:
                start_date = start_date_part
            
            end_date_part = parts[1].strip()
            if len(end_date_part) == 4:
                end_date = f"{end_date_part}-01"
            else:
                end_date = end_date_part
        else:
            if len(time_period) == 4:
                start_date = f"{time_period}-01"
            else:
                start_date = time_period

        # 整理描述
        desc_lines = []
        for line in desc_block.splitlines():
            line_str = line.strip()
            if line_str.startswith("-") or line_str.startswith("*"):
                bullet_content = re.sub(r"^[-*]\s*", "", line_str).strip()
                desc_lines.append(f"• {bullet_content}")
            elif line_str:
                desc_lines.append(line_str)
        
        experiences.append({
            "company": company,
            "title": title,
            "location": "",
            "start_date": start_date,
            "end_date": end_date,
            "description": "\n".join(desc_lines)
        })

    if experiences:
        profile["experiences"] = experiences
        primary_title = experiences[0]["title"]
        skills_summary = "Python, FastAPI, Next.js"
        if skills:
            skills_summary = skills[0]
        profile["headline"] = f"{primary_title} | 專注於 {skills_summary}"
        
        about_parts = [f"熱愛解決問題的{primary_title}。"]
        if skills:
            about_parts.append(f"擅長 {'、'.join(skills)}。")
        profile["about"] = "".join(about_parts)

    return profile

def parse_skill_markdown(content: str, filename: str) -> SkillItem:
    """解析技能 Markdown 卡片內容以提取 LinkedIn 所需的技能特徵。"""
    # 預設值
    name = Path(filename).stem.replace("_", " ")
    proficiency = "良好"
    core_tech = ""
    description = ""

    # 解析 Frontmatter title
    title_match = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
    if title_match:
        name = title_match.group(1).strip()

    # 搜尋 核心描述、熟練程度、核心技術
    # 支持中文與英文冒號以及可能有的空格
    desc_match = re.search(r"-\s*\*\*核心描述\*\*[:：]\s*(.+)$", content, re.MULTILINE)
    prof_match = re.search(r"-\s*\*\*熟練程度\*\*[:：]\s*(.+)$", content, re.MULTILINE)
    tech_match = re.search(r"-\s*\*\*核心技術\*\*[:：]\s*(.+)$", content, re.MULTILINE)

    if desc_match:
        description = desc_match.group(1).strip()
    if prof_match:
        proficiency = prof_match.group(1).strip()
    if tech_match:
        core_tech = tech_match.group(1).strip()

    # 如果沒有找到核心描述，用第一段非 frontmatter 文字代替
    if not description:
        lines = content.splitlines()
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("---") and not stripped.startswith("title:") and not stripped.startswith("tags:") and not stripped.startswith("created_at:"):
                # 去除 markdown 語法
                clean_line = re.sub(r"[\*#`_\-\[\]\(\)]", "", stripped)
                description = clean_line[:150]
                break

    return SkillItem(
        name=name,
        proficiency=proficiency,
        core_tech=core_tech,
        description=description
    )

def get_profile_path() -> Path:
    return settings.vault_dir / "linkedin_profile.json"

@router.get("", response_model=LinkedInProfileResponse)
async def get_linkedin_profile():
    """獲取 LinkedIn 個人資料，並動態整合技能庫資料。"""
    profile_path = get_profile_path()
    
    # 決定是否需要初始化/覆寫 (不存在，或是名字是「吳奕霆」)
    need_initialize = not profile_path.exists()
    
    profile_data = None
    if profile_path.exists():
        try:
            content = profile_path.read_text(encoding="utf-8")
            profile_data = json.loads(content)
            if profile_data.get("name") == "吳奕霆":
                need_initialize = True
        except Exception as exc:
            logger.error("解析 linkedin_profile.json 失敗: %s", exc)
            profile_data = DEFAULT_PROFILE.copy()

    if need_initialize:
        # 嘗試從 resume.md 解析
        resume_path = settings.init_dir / "resume.md"
        resolved_profile = None
        if resume_path.exists():
            try:
                resume_content = resume_path.read_text(encoding="utf-8")
                resolved_profile = parse_resume_markdown(resume_content)
            except Exception as exc:
                logger.error("解析 resume.md 失敗: %s", exc)
        
        if not resolved_profile:
            resolved_profile = DEFAULT_PROFILE.copy()
        
        # 保存到 json 中
        try:
            settings.vault_dir.mkdir(parents=True, exist_ok=True)
            profile_path.write_text(json.dumps(resolved_profile, ensure_ascii=False, indent=2), encoding="utf-8")
            profile_data = resolved_profile
        except Exception as exc:
            logger.error("寫入 linkedin_profile.json 失敗: %s", exc)
            profile_data = resolved_profile

    # 2. 獲取並解析 vault/skills/*.md 的技能資料
    skills_list = []
    skills_dir = settings.vault_dir / "skills"
    if skills_dir.exists():
        for filepath in sorted(skills_dir.glob("*.md")):
            if filepath.name == ".gitkeep":
                continue
            try:
                content = filepath.read_text(encoding="utf-8")
                skill_item = parse_skill_markdown(content, filepath.name)
                # 排除像 "技能 Wiki 架構概要" 這種管理性質卡片
                if "架構概要" not in skill_item.name:
                    skills_list.append(skill_item)
            except Exception as exc:
                logger.error("讀取技能 Markdown 失敗 %s: %s", filepath.name, exc)

    return LinkedInProfileResponse(
        name=profile_data.get("name", DEFAULT_PROFILE["name"]),
        headline=profile_data.get("headline", DEFAULT_PROFILE["headline"]),
        location=profile_data.get("location", DEFAULT_PROFILE["location"]),
        about=profile_data.get("about", DEFAULT_PROFILE["about"]),
        experiences=profile_data.get("experiences", DEFAULT_PROFILE["experiences"]),
        educations=profile_data.get("educations", DEFAULT_PROFILE["educations"]),
        skills=skills_list
    )

@router.put("")
async def update_linkedin_profile(profile: LinkedInProfile):
    """更新 LinkedIn 個人檔案資料 (基本資料與經歷)。"""
    profile_path = get_profile_path()
    try:
        settings.vault_dir.mkdir(parents=True, exist_ok=True)
        # 轉換為 dict 並寫入 JSON 檔案
        data_to_save = profile.model_dump()
        profile_path.write_text(json.dumps(data_to_save, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"status": "success", "message": "LinkedIn 個人資料更新成功"}
    except Exception as exc:
        logger.error("更新 linkedin_profile.json 失敗: %s", exc)
        raise HTTPException(status_code=500, detail=f"儲存個人檔案失敗: {exc}")
