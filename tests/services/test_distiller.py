import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path
import tempfile
import shutil

from pro_copilot.services.distiller import _parse_sections, run_weekly_distillation, _extract_frontmatter

class TestDistiller(unittest.IsolatedAsyncioTestCase):
    def test_parse_sections(self):
        sample_text = (
            "## [新增] Python 程式設計\n"
            "## 技能說明\n"
            "- **核心描述**：使用 Python 進行開發。\n"
            "- **熟練程度**：熟練\n"
            "- **核心技術**：FastAPI\n\n"
            "## 實際專案紀錄\n"
            "### 專案 A\n"
            "- **情境 (Situation)**：需要 API。\n"
            "- **結果 (Result)**：完成。\n\n"
            "## [更新] Docker 部署\n"
            "## 技能說明\n"
            "- **核心描述**：容器化部署。\n"
            "- **熟練程度**：熟練\n"
            "- **核心技術**：Docker Compose\n\n"
            "## 實際專案紀錄\n"
            "### 專案 B\n"
            "- **情境 (Situation)**：需要部署。\n"
            "- **結果 (Result)**：完成。\n"
        )
        sections = _parse_sections(sample_text)
        self.assertEqual(len(sections), 2)
        
        self.assertEqual(sections[0][0], "Python 程式設計")
        self.assertFalse(sections[0][2])  # is_update = False
        self.assertIn("## 技能說明", sections[0][1])
        
        self.assertEqual(sections[1][0], "Docker 部署")
        self.assertTrue(sections[1][2])  # is_update = True
        self.assertIn("## 實際專案紀錄", sections[1][1])

    def test_extract_frontmatter(self):
        content_with_fm = (
            "---\n"
            "title: Python\n"
            "tags: [技能, Python]\n"
            "created_at: 2026-07-11\n"
            "---\n\n"
            "## 技能說明\n"
        )
        fm = _extract_frontmatter(content_with_fm)
        self.assertIn("title: Python", fm)
        self.assertTrue(fm.startswith("---"))
        self.assertTrue(fm.endswith("---\n"))

        content_no_fm = "## 技能說明\n"
        fm_empty = _extract_frontmatter(content_no_fm)
        self.assertEqual(fm_empty, "")

    @patch("pro_copilot.services.distiller.call_llm", new_callable=AsyncMock)
    @patch("pro_copilot.services.distiller.run_document_conversion", new_callable=AsyncMock)
    @patch("pro_copilot.services.distiller.settings")
    async def test_run_weekly_distillation(self, mock_settings, mock_doc_conv, mock_call_llm):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            raw_logs_dir = temp_path / "raw_logs"
            vault_dir = temp_path / "vault"
            
            raw_logs_dir.mkdir(parents=True)
            (raw_logs_dir / "voice").mkdir(parents=True)
            vault_dir.mkdir(parents=True)
            
            # 設定 mock 屬性
            mock_settings.raw_logs_dir = raw_logs_dir
            mock_settings.vault_dir = vault_dir
            
            # 建立原始工作日誌與既有技能檔案
            # 既有技能
            existing_skills_dir = vault_dir / "skills"
            existing_skills_dir.mkdir(parents=True)
            existing_file = existing_skills_dir / "docker_部署.md"
            existing_file.write_text(
                "---\n"
                "title: Docker 部署\n"
                "tags: [技能, Docker]\n"
                "created_at: 2026-07-11\n"
                "---\n\n"
                "## 技能說明\n"
                "- **核心描述**：舊描述\n"
                "- **熟練程度**：熟悉\n",
                encoding="utf-8"
            )
            
            # 模擬新日誌
            new_log = raw_logs_dir / "voice" / "note.md"
            new_log.write_text("新學會了 Docker Compose 網路設定", encoding="utf-8")
            
            # Mock LLM 回傳的合併更新內容
            mock_call_llm.return_value = (
                "## [更新] Docker 部署\n"
                "## 技能說明\n"
                "- **核心描述**：更新描述\n"
                "- **熟練程度**：熟練\n"
                "- **核心技術**：Docker Compose\n\n"
                "## 實際專案紀錄\n"
                "### 專案 C\n"
                "- **情境 (Situation)**：設定網路。\n"
                "- **結果 (Result)**：完成。\n"
            )
            
            await run_weekly_distillation()
            
            # 驗證既有技能檔案是否被完全更新，且保留了原本的 frontmatter
            updated_content = existing_file.read_text(encoding="utf-8")
            self.assertIn("created_at: 2026-07-11", updated_content)
            self.assertIn("- **核心描述**：更新描述", updated_content)
            self.assertIn("## 實際專案紀錄", updated_content)
            self.assertNotIn("## 更新 (", updated_content)  # 不應出現舊有的尾端追加格式
