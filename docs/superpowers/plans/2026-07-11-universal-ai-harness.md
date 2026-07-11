# Universal AI Development Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立工具中立、可由 JSON 狀態與自動驗證器約束的標準 AI 開發流程。

**Architecture:** 根目錄協定文件作為單一入口，JSON Schema 與範例固定跨工具資料格式，無外部依賴的 Python CLI 負責初始化及驗證。驗證器只判斷紀錄是否通過門檻，不執行任意工作命令。

**Tech Stack:** Markdown、JSON Schema 2020-12、Python 3.14 標準函式庫、`unittest`、Docker Compose。

## Global Constraints

- 一律使用繁體中文文件。
- 不綁定任何 AI 供應商或代理 SDK。
- 不新增 Python 執行期依賴。
- 測試與驗證在 Docker Compose 一次性容器內執行，不在宿主機啟動伺服器。

---

### Task 1: 狀態契約與失敗測試

**Files:**
- Create: `.harness/schema.json`
- Create: `.harness/task.example.json`
- Create: `tests/test_harness.py`

**Interfaces:**
- Produces: `scripts/harness.py init <path>` 與 `scripts/harness.py check <path>` 的外部行為契約。

- [ ] 建立最小範例與 JSON Schema，固定階段及欄位名稱。
- [ ] 撰寫 CLI 初始化、無效完成狀態、有效完成狀態測試。
- [ ] 在容器執行 `python -m unittest tests.test_harness -v`，預期因 CLI 尚不存在而失敗。

### Task 2: 最小驗證 CLI

**Files:**
- Create: `scripts/harness.py`
- Test: `tests/test_harness.py`

**Interfaces:**
- Consumes: `.harness/task.example.json`。
- Produces: `init` 建立狀態檔；`check` 成功回傳 0、失敗回傳 1 並列出全部錯誤。

- [ ] 實作 JSON 載入、基本欄位與階段累積門檻檢查。
- [ ] 實作安全初始化，既有目標檔不得覆寫。
- [ ] 在容器重跑單元測試，預期全部通過。

### Task 3: 專案入口與整體驗證

**Files:**
- Create: `HARNESS.md`
- Modify: `README.md`
- Modify: `docs/CONTRIBUTING.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: CLI 與狀態契約。
- Produces: 任何 AI 工具可依循的讀取順序、階段規則及容器命令。

- [ ] 記錄協定、角色分工、階段門檻、失敗處理與標準命令。
- [ ] 從 README 與貢獻指南連結 harness，並記錄未發布變更。
- [ ] 執行完整單元測試及範例狀態檢查，預期兩者皆成功。
- [ ] 檢查 diff 僅包含本需求所需檔案。
