# Discovering Missing Features Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立一個可重複執行、以證據為基礎的專案缺失功能探索 prompt workflow。

**Architecture:** 使用單一 `.github/prompts/discover-missing-features.prompt.md` 定義探索漏斗與固定輸出契約。工作流只讀取專案資訊並產生提案，不自動修改產品規劃或程式碼。

**Tech Stack:** Markdown、YAML、GitHub Copilot prompt files

## Global Constraints

- 所有對使用者的溝通與輸出使用繁體中文。
- 只建立必要的技能檔案，不新增腳本、資產或無關文件。
- 不直接修改 roadmap、建立 issue 或開始實作，除非使用者明確要求。

---

### Task 1: 建立並驗證缺失功能探索工作流

**Files:**
- Create: `.github/prompts/discover-missing-features.prompt.md`

**Interfaces:**
- Consumes: 專案文件、原始碼結構、測試與近期 Git 歷史。
- Produces: 現況摘要、缺口地圖、候選比較、推薦前三名與首選功能簡報。

- [ ] **Step 1: 建立失敗檢查**

確認 `.github/prompts/discover-missing-features.prompt.md` 尚不存在，預期檢查因工作流缺失而失敗。

- [ ] **Step 2: 寫入最小工作流**

在 prompt file 寫入觸發條件、證據盤點、核心旅程、多視角發想、過濾、排序、收斂與固定輸出契約。

- [ ] **Step 3: 執行格式驗證**

確認檔案具有 YAML frontmatter、非空描述與 Markdown 主體。

- [ ] **Step 4: 執行契約檢查**

確認技能文字包含現況快照、核心旅程、候選功能、影響力、信心、成本、風險、推薦前三名、最小範圍、驗收條件與假設標記。

- [ ] **Step 5: 自我審查差異**

檢查 `git diff`，確認變更只包含設計、計畫與技能檔案，且沒有 `TODO`、`TBD` 或未授權的自動寫入步驟。
