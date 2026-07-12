import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from pro_copilot.main import app
from pro_copilot.api.linkedin import DEFAULT_PROFILE

class TestLinkedInAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # 建立假的 skills 目錄與檔案
        self.skills_dir = self.temp_path / "skills"
        self.skills_dir.mkdir(parents=True)
        
        # 寫入一個測試用的技能卡片
        self.skill_file = self.skills_dir / "python_fastapi.md"
        self.skill_file.write_text(
            "---\n"
            "title: Python & FastAPI 開發\n"
            "tags: [技能, Python]\n"
            "created_at: 2026-07-11\n"
            "---\n\n"
            "## 技能說明\n"
            "- **核心描述**：使用 Python FastAPI 建構高效 API。\n"
            "- **熟練程度**：精通\n"
            "- **核心技術**：FastAPI, Python, Asyncio\n",
            encoding="utf-8"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("pro_copilot.api.linkedin.settings")
    def test_get_linkedin_profile_creates_default(self, mock_settings):
        # 模擬設定的 vault_dir 指向臨時目錄
        mock_settings.vault_dir = self.temp_path
        
        # 呼叫 GET
        response = self.client.get("/api/linkedin")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["name"], DEFAULT_PROFILE["name"])
        self.assertEqual(data["headline"], DEFAULT_PROFILE["headline"])
        
        # 驗證動態技能是否有被解析出來
        self.assertEqual(len(data["skills"]), 1)
        self.assertEqual(data["skills"][0]["name"], "Python & FastAPI 開發")
        self.assertEqual(data["skills"][0]["proficiency"], "精通")
        self.assertEqual(data["skills"][0]["core_tech"], "FastAPI, Python, Asyncio")
        self.assertEqual(data["skills"][0]["description"], "使用 Python FastAPI 建構高效 API。")
        
        # 驗證 linkedin_profile.json 是否有被建立在臨時目錄
        profile_json = self.temp_path / "linkedin_profile.json"
        self.assertTrue(profile_json.exists())

    @patch("pro_copilot.api.linkedin.settings")
    def test_update_linkedin_profile(self, mock_settings):
        mock_settings.vault_dir = self.temp_path
        
        # 建立新的個人檔案資料
        payload = {
            "name": "測試名",
            "headline": "測試頭銜",
            "location": "測試地區",
            "about": "測試關於我",
            "experiences": [
                {
                    "company": "測試公司",
                    "title": "測試職稱",
                    "location": "測試地點",
                    "start_date": "2025-01",
                    "end_date": "2025-12",
                    "description": "測試經歷描述"
                }
            ],
            "educations": [
                {
                    "school": "測試學校",
                    "degree": "測試學位",
                    "start_date": "2020",
                    "end_date": "2024"
                }
            ]
        }
        
        # 呼叫 PUT 更新
        put_response = self.client.put("/api/linkedin", json=payload)
        self.assertEqual(put_response.status_code, 200)
        self.assertEqual(put_response.json()["status"], "success")
        
        # 再呼叫 GET 驗證資料是否已經更新
        get_response = self.client.get("/api/linkedin")
        self.assertEqual(get_response.status_code, 200)
        
        data = get_response.json()
        self.assertEqual(data["name"], "測試名")
        self.assertEqual(data["headline"], "測試頭銜")
        self.assertEqual(data["location"], "測試地區")
        self.assertEqual(data["about"], "測試關於我")
        self.assertEqual(data["experiences"][0]["company"], "測試公司")
        self.assertEqual(data["experiences"][0]["description"], "測試經歷描述")
        self.assertEqual(data["educations"][0]["school"], "測試學校")
