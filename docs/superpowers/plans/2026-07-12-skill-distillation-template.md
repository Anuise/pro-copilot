# 技能卡片模板化與 AI 蒸餾流程重構實作計畫 (Skill Template & Distillation Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 重構技能蒸餾分析的 LLM Prompt 與寫入邏輯，導入包含「技能說明」與「專案紀錄」的固定 Obsidian 模板。

**Architecture:**
- 修改 `src/pro_copilot/services/distiller.py` 中的 `SYSTEM_PROMPT`，強制 LLM 以結構化模版輸出完整合併的內容。
- 修改 `run_weekly_distillation`，在更新卡片時提取並保留既有的 YAML Frontmatter，並使用 LLM 合併輸出的最新 body 直接覆寫檔案。
- 建立 `tests/services/test_distiller.py` 對該服務進行單元與模擬整合測試。

**Tech Stack:** Python, unittest, mock

## Global Constraints

- 一律使用繁體中文。
- 專案內部變更須符合 `pro_copilot` 的套件與 API 設計。
- 測試運行一律在 Docker 容器或本地使用 Python 虛擬環境指令，不佔用系統連接埠。

---

### Task 1: 建立 distiller 單元與整合測試

**Files:**
- Create: `tests/services/test_distiller.py`

**Interfaces:**
- Consumes: [src/pro_copilot/services/distiller.py](file:///E:/program/pro-copilot/src/pro_copilot/services/distiller.py) 內部的函數 `_parse_sections` 與 `run_weekly_distillation`。
- Produces: 驗證解析器與覆寫邏輯在模擬環境中的正確性。

- [ ] **Step 1: 撰寫 distiller 的單元測試 (含失敗案例與 mock)**
  
  在宿主機建立 `tests/services/test_distiller.py`，內容如下：

  ```python
  import unittest
  from unittest.mock import patch, AsyncMock, MagicMock
  from pathlib import Path
  import tempfile
  import shutil

  from pro_copilot.services.distiller import _parse_sections, run_weekly_distillation, _extract_frontmatter

  class TestDistiller(unittest.TestCase):
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
  ```

- [ ] **Step 2: 執行測試並驗證失敗 (因為 distiller 尚未引入 _extract_frontmatter 與新覆寫邏輯)**
  
  Run: `uv run python -m unittest tests.services.test_distiller -v`
  Expected: FAIL (提示 `ImportError: cannot import name '_extract_frontmatter'`)

- [ ] **Step 3: 暫存 Commit**
  
  ```bash
  git add tests/services/test_distiller.py
  git commit -m "test: add distiller template and overwrite unit tests"
  ```

---

### Task 2: 重構 distiller 系統提示與覆寫合併邏輯

**Files:**
- Modify: `src/pro_copilot/services/distiller.py`

**Interfaces:**
- Consumes: [src/pro_copilot/services/distiller.py](file:///E:/program/pro-copilot/src/pro_copilot/services/distiller.py)
- Produces: 通過 Task 1 測試的模組程式碼。

- [ ] **Step 1: 修改 SYSTEM_PROMPT 並實作合併覆寫邏輯**
  
  在 `src/pro_copilot/services/distiller.py` 中進行以下修改：
  
  1. 新增 `_extract_frontmatter` 輔助函數與導入 `re`（若未導入）。
  2. 重構 `SYSTEM_PROMPT` 以強制規定 Markdown 模板。
  3. 修改 `run_weekly_distillation` 中 `filepath.exists() and is_update` 區段，進行 frontmatter 提取與覆寫寫入。

  具體修改對照（[distiller.py](file:///E:/program/pro-copilot/src/pro_copilot/services/distiller.py)）：

  ```python
  # 修改 SYSTEM_PROMPT (第 12-25 行左右)
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
  ```

  ```python
  # 新增函數與修改 run_weekly_distillation (約第 69-92 行)
  import re

  def _extract_frontmatter(content: str) -> str:
      """從 Markdown 內容中提取 YAML frontmatter。如果沒有則回傳空字串。"""
      match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
      if match:
          return match.group(0)
      return ""

  # 在 run_weekly_distillation 循環中：
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
  ```

- [ ] **Step 2: 執行測試並驗證通過**
  
  Run: `uv run python -m unittest tests.services.test_distiller -v`
  Expected: PASS

- [ ] **Step 3: 執行通用測試與驗證 (Harness 本身與其他測試)**
  
  Run: `uv run python -m unittest tests.test_harness -v`
  Expected: PASS

- [ ] **Step 4: 提交變更**
  
  ```bash
  git add src/pro_copilot/services/distiller.py
  git commit -m "feat: improve skill distillation template and implement full overwrite merge"
  ```
