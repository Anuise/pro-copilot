# Pro-Copilot Open-Source Roadmap Tracking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立公開 roadmap 與 GitHub 原生需求追蹤機制，讓每個新功能從提案、評估、設計、實作、驗收到發布都可追溯。

**Architecture:** 以 `ROADMAP.md` 管理產品方向與完成條件，以 GitHub Issue Forms 收集結構化需求，以 GitHub Project 管理工作狀態與時程，再由 RFC、Pull Request 與 changelog 串接設計、交付及發布證據。所有檔案均為文件或 GitHub metadata，不修改執行期產品程式碼。

**Tech Stack:** Markdown、GitHub Issue Forms YAML、GitHub Projects、GitHub Pull Requests

## Global Constraints

- 所有對外文件使用繁體中文。
- 第一個公開版本維持單人自架與 Docker Compose 部署。
- Roadmap 使用 `Now / Next / Later`，不承諾固定日期。
- `Status` 固定為 `Inbox / Triaged / Planned / In Progress / Review / Done`。
- `Horizon` 固定為 `Now / Next / Later / Not Planned`。
- GitHub Project 的 `Status` 是唯一工作流程狀態來源。
- `ROADMAP.md` 只追蹤產品成果，不列出所有細項 Issue。
- 不修改使用者現有的 `vault/skills` 變更。

---

### Task 1: 公開 Roadmap 與 Changelog

**Files:**
- Create: `ROADMAP.md`
- Create: `CHANGELOG.md`

**Interfaces:**
- Consumes: `docs/superpowers/specs/2026-07-11-open-source-roadmap-design.md` 的產品方向、階段與完成條件。
- Produces: 後續 Issue 與 Project item 可引用的 `Now / Next / Later` 成果定義，以及已發布變更的唯一紀錄入口。

- [ ] **Step 1: 建立公開 roadmap**

建立 `ROADMAP.md`：

```markdown
# Pro-Copilot Roadmap

Pro-Copilot 的目標是成為可自行部署、可追溯工作成果，並能從個人資料生成客製履歷的開源 AI 職涯副駕駛。

本 roadmap 使用 `Now / Next / Later` 表達優先順序，不承諾固定日期。具體工作、負責人與進度由 GitHub Issues 和 GitHub Project 追蹤。

## 產品原則

- 第一個公開版本服務單一使用者，透過 Docker Compose 自行部署。
- 同時照顧希望直接使用產品的個人，以及希望擴充整合的開發者。
- 優先建立可重現、可測試、可復原的基線，再增加新功能。
- AI 產出必須可追溯來源；重要資料變更應能由使用者確認。

## Now：可信賴的開源基線

**成果：** 陌生使用者能依文件完成部署，開發者能安全修改並驗證變更。

- 統一 Docker Compose 安裝與執行文件。
- 建立後端測試、前端 E2E 與無付費 API 的 smoke test。
- 建立 lint、測試、映像建置與 Compose 驗證的 GitHub Actions。
- 驗證必要設定，避免 mock 或靜默降級被誤認為正式結果。
- 保護 webhook、檔案上傳、憑證與 API 錯誤資訊。
- 建立資料庫 migration、範例資料、貢獻流程與發布紀錄。

### Now 完成條件

- 全新環境可只依 README 使用 Docker Compose 啟動必要服務。
- CI 可驗證 lint、測試、建置與基礎服務健康狀態。
- smoke test 不需真實付費 API，且失敗訊息可指出缺少的設定或服務。
- 敏感設定不會進入版本庫、一般 API 回應或預設日誌。

## Next：第一次成功旅程

**成果：** 非開發者可透過 Web UI 完成「資料輸入 → 技能蒸餾 → 履歷輸出」。

- 建立首次設定與外部服務連線檢查。
- 顯示資料來源同步狀態、最近成功時間與可操作錯誤。
- 支援蒸餾預覽、人工確認與安全寫入。
- 改善技能去重、來源引用與更新歷史。
- 提供 JD 匯入、履歷版本比較與標準格式匯出。
- 提供長時間任務進度、失敗重試、備份、還原與資料匯出。

### Next 完成條件

- 新使用者不需執行應用程式 CLI，即可透過 Web UI 完成核心旅程。
- 技能更新可追溯到來源紀錄與確認動作。
- 履歷可追溯到職缺描述與使用的技能來源。
- 備份可在乾淨環境還原並通過核心旅程驗證。

## Later：擴充與社群生態

**成果：** 外部貢獻者能新增資料來源或 AI provider，而不需修改核心流程。

- 定義資料來源 adapter 或 plugin 介面。
- 評估 GitHub、Notion、Jira 等資料來源。
- 支援替換 LLM 與 embedding provider。
- 建立技能 schema、匯入匯出格式與相容性版本。
- 提供外掛範例、開發文件與貢獻者測試工具。
- 建立文件網站、範例展示與社群治理規則。
- 評估桌面封裝、離線模型與多人模式。

`Later` 代表方向一致但尚未承諾，仍須通過功能需求與 RFC 流程。

## 暫不納入首版

- 登入、帳號管理與多租戶。
- 官方雲端託管與付費機制。
- 原生行動 App。

## 如何提出新功能

請使用 GitHub 的 Feature Request 表單。小型功能經分流後可直接規劃；跨模組、改變資料格式、引入基礎設施或涉及安全與隱私的功能，必須先完成 RFC。

完整流程請參考 [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) 與 [`docs/rfcs/README.md`](docs/rfcs/README.md)。
```

- [ ] **Step 2: 建立 changelog**

建立 `CHANGELOG.md`：

```markdown
# Changelog

本檔案記錄 Pro-Copilot 已發布的使用者可見變更，格式依循 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.1.0/)，版本號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## [Unreleased]

### Added

- 建立公開 roadmap 與 GitHub 需求追蹤流程。

### Changed

### Deprecated

### Removed

### Fixed

### Security
```

- [ ] **Step 3: 驗證 roadmap 與 changelog 結構**

Run:

```powershell
$roadmap = Get-Content -Raw ROADMAP.md
$required = @('## Now：', '## Next：', '## Later：', '### Now 完成條件', '### Next 完成條件', '## 如何提出新功能')
$missing = $required | Where-Object { -not $roadmap.Contains($_) }
if ($missing) { throw "ROADMAP 缺少章節: $($missing -join ', ')" }
$changelog = Get-Content -Raw CHANGELOG.md
if (-not $changelog.Contains('## [Unreleased]')) { throw 'CHANGELOG 缺少 Unreleased 章節' }
```

Expected: 命令無輸出並以 exit code `0` 結束。

- [ ] **Step 4: 檢查文件差異**

Run: `git diff --check -- ROADMAP.md CHANGELOG.md`

Expected: 無 whitespace error。

- [ ] **Step 5: Commit**

```bash
git add ROADMAP.md CHANGELOG.md
git commit -m "docs: add public product roadmap"
```

### Task 2: GitHub Issue Intake

**Files:**
- Create: `.github/ISSUE_TEMPLATE/feature_request.yml`
- Create: `.github/ISSUE_TEMPLATE/bug_report.yml`
- Create: `.github/ISSUE_TEMPLATE/config.yml`

**Interfaces:**
- Consumes: `type:*`、`area:*`、`priority:*`、`attention:*`、`impact:*` label namespace。
- Produces: 可被 triage 的結構化功能需求與錯誤報告；新需求預設帶有 `attention:triage`，但工作流程階段仍只由 GitHub Project `Status` 表示。

- [ ] **Step 1: 建立 Feature Request Issue Form**

建立 `.github/ISSUE_TEMPLATE/feature_request.yml`：

```yaml
name: 功能需求
description: 提議能解決明確使用者問題的新功能或改善
title: "[Feature]: "
labels:
  - "type:feature"
  - "attention:triage"
body:
  - type: markdown
    attributes:
      value: |
        感謝你提出功能需求。請先描述問題與成功條件，不要只描述預想解法。
  - type: textarea
    id: problem
    attributes:
      label: 問題與受影響使用者
      description: 誰在什麼情境遇到什麼問題？
      placeholder: 身為…，當…時，我無法…，因此…
    validations:
      required: true
  - type: textarea
    id: workaround
    attributes:
      label: 目前替代方式
      description: 目前如何處理？替代方式有什麼不足？
    validations:
      required: true
  - type: textarea
    id: outcome
    attributes:
      label: 預期成果與成功條件
      description: 完成後應能觀察到什麼結果？請使用可驗證的敘述。
    validations:
      required: true
  - type: textarea
    id: acceptance
    attributes:
      label: 驗收情境
      description: 維護者應如何重現並確認功能有效？
      placeholder: |
        1. 給定…
        2. 當…
        3. 則…
    validations:
      required: true
  - type: textarea
    id: non_goals
    attributes:
      label: 不處理的範圍
      description: 這項需求明確不包含什麼？
    validations:
      required: true
  - type: checkboxes
    id: impact
    attributes:
      label: 可能影響
      description: 勾選所有可能受影響的項目；不確定時可不勾選並在補充資訊說明。
      options:
        - label: 隱私或個人資料
        - label: 安全或權限
        - label: 資料格式或資料遷移
        - label: 公開 API 或向後相容性
        - label: 新增長期運行服務或外部依賴
  - type: textarea
    id: impact_analysis
    attributes:
      label: 影響分析
      description: 請分別說明隱私、安全、資料遷移與相容性為「有／無／不確定」，並提供理由。
      placeholder: |
        隱私：無，理由是…
        安全：不確定，需要確認…
        資料遷移：有，需要…
        相容性：無，理由是…
    validations:
      required: true
  - type: textarea
    id: additional
    attributes:
      label: 補充資訊
      description: 可附上流程、畫面、連結或替代方案。
  - type: checkboxes
    id: checks
    attributes:
      label: 提交前確認
      options:
        - label: 我已搜尋現有 Issues，確認沒有重複需求。
          required: true
        - label: 我理解提交需求不代表已承諾排程或實作。
          required: true
```

- [ ] **Step 2: 建立 Bug Report Issue Form**

建立 `.github/ISSUE_TEMPLATE/bug_report.yml`：

```yaml
name: 錯誤回報
description: 回報可重現的錯誤、回歸或非預期行為
title: "[Bug]: "
labels:
  - "type:bug"
  - "attention:triage"
body:
  - type: markdown
    attributes:
      value: |
        請勿貼上 API key、token、履歷內容或其他個人資料。安全漏洞請依安全政策私下回報。
  - type: textarea
    id: summary
    attributes:
      label: 問題摘要
      description: 清楚描述實際發生的錯誤。
    validations:
      required: true
  - type: textarea
    id: steps
    attributes:
      label: 重現步驟
      placeholder: |
        1. 使用 Docker Compose 啟動…
        2. 前往…
        3. 執行…
        4. 看到…
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: 預期行為
    validations:
      required: true
  - type: textarea
    id: actual
    attributes:
      label: 實際行為與錯誤訊息
      description: 貼上已移除密鑰與個人資料的錯誤資訊。
    validations:
      required: true
  - type: input
    id: version
    attributes:
      label: Pro-Copilot 版本或 commit
      placeholder: v1.0.0 或 commit SHA
    validations:
      required: true
  - type: dropdown
    id: environment
    attributes:
      label: 執行環境
      options:
        - Docker Compose
        - GitHub Codespaces
        - 其他容器環境
    validations:
      required: true
  - type: input
    id: platform
    attributes:
      label: 作業系統與瀏覽器
      placeholder: Windows 11 / Docker Desktop / Chrome 版本
    validations:
      required: true
  - type: textarea
    id: logs
    attributes:
      label: 已去除敏感資訊的日誌
      render: shell
  - type: checkboxes
    id: checks
    attributes:
      label: 提交前確認
      options:
        - label: 我已搜尋現有 Issues，確認沒有重複回報。
          required: true
        - label: 我已移除 API key、token、履歷內容與其他個人資料。
          required: true
```

- [ ] **Step 3: 設定 Issue template chooser**

建立 `.github/ISSUE_TEMPLATE/config.yml`：

```yaml
blank_issues_enabled: false
contact_links:
  - name: 私下回報安全漏洞
    url: https://github.com/Anuise/pro-copilot/security/advisories/new
    about: 請勿公開敏感漏洞；使用 GitHub Private Vulnerability Reporting。
```

- [ ] **Step 4: 驗證 Issue Forms 必要欄位**

Run:

```powershell
$feature = Get-Content -Raw .github/ISSUE_TEMPLATE/feature_request.yml
$featureIds = @('id: problem', 'id: workaround', 'id: outcome', 'id: acceptance', 'id: non_goals', 'id: impact', 'id: impact_analysis')
$missingFeature = $featureIds | Where-Object { -not $feature.Contains($_) }
if ($missingFeature) { throw "Feature Request 缺少欄位: $($missingFeature -join ', ')" }
$bug = Get-Content -Raw .github/ISSUE_TEMPLATE/bug_report.yml
$bugIds = @('id: summary', 'id: steps', 'id: expected', 'id: actual', 'id: version', 'id: environment')
$missingBug = $bugIds | Where-Object { -not $bug.Contains($_) }
if ($missingBug) { throw "Bug Report 缺少欄位: $($missingBug -join ', ')" }
```

Expected: 命令無輸出並以 exit code `0` 結束。

- [ ] **Step 5: 檢查 YAML 與 whitespace**

Run: `git diff --check -- .github/ISSUE_TEMPLATE`

Expected: 無 whitespace error；人工核對所有 `body` 項目都有 GitHub Issue Forms 支援的 `type`，所有必要輸入都有 `validations.required: true`。

- [ ] **Step 6: Commit**

```bash
git add .github/ISSUE_TEMPLATE
git commit -m "docs: add structured issue intake"
```

### Task 3: 貢獻、RFC 與 Pull Request 追蹤

**Files:**
- Create: `docs/CONTRIBUTING.md`
- Create: `docs/rfcs/README.md`
- Create: `.github/pull_request_template.md`
- Create: `SECURITY.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: Task 1 的 roadmap 階段、Task 2 的 Feature Request 與 Bug Report。
- Produces: 從 triage、RFC、Project、PR 到 release 的完整流程，以及 README 對外入口。

- [ ] **Step 1: 建立貢獻流程**

建立 `docs/CONTRIBUTING.md`：

```markdown
# 貢獻指南

感謝你協助改進 Pro-Copilot。本專案同時處理個人工作紀錄、AI 產出與外部服務整合，因此所有變更都必須可追溯、可測試，且不得暴露敏感資料。

## 開始之前

- 錯誤請使用 Bug Report。
- 新功能或行為變更請使用 Feature Request。
- 不要在公開 Issue、Pull Request 或日誌貼上 API key、token、履歷內容、語音內容或其他個人資料。
- 安全漏洞請依 [`SECURITY.md`](../SECURITY.md) 使用 GitHub Private Vulnerability Reporting 私下回報。
- 實作前先確認 Issue 已完成 triage；大型或高風險功能需先核准 RFC。

## 需求生命週期

1. 新 Issue 進入 `Inbox`。
2. 維護者確認問題、重複性、範圍、風險與驗收條件後移至 `Triaged`。
3. 需要 RFC 的功能先標記 `attention:design`；RFC 核准後才能進入 `Planned`。
4. 已有負責人並開始實作時進入 `In Progress`。
5. Pull Request 與驗收進行中時進入 `Review`。
6. 變更進入正式 release、文件與 changelog 均更新後進入 `Done`。

GitHub Project 的 `Status` 是唯一工作流程狀態來源。Labels 只用於類型、模組、優先級與影響查詢。

## Roadmap 時程

- `Now`：目前優先完成的成果。
- `Next`：Now 完成後的候選成果。
- `Later`：方向一致但尚未承諾。
- `Not Planned`：目前不符合方向或成本效益，Issue 需保留決策理由。

詳細方向與完成條件請參考 [`ROADMAP.md`](../ROADMAP.md)。

## 何時需要 RFC

符合任一條件即需 RFC：

- 同時改變前端與後端的主要流程。
- 改變資料格式、資料庫 schema、技能 schema 或公開介面。
- 引入新的基礎設施、長期運行服務或外部依賴。
- 涉及破壞性變更、安全、隱私或資料遷移。
- 建立供外掛或第三方整合依賴的擴充介面。

格式與流程請參考 [`docs/rfcs/README.md`](rfcs/README.md)。

## Labels

- `type:*`：`feature`、`bug`、`docs`、`maintenance`、`security`。
- `area:*`：`frontend`、`api`、`ai`、`ingestion`、`storage`、`devops`、`docs`。
- `priority:*`：`critical`、`high`、`medium`、`low`。
- `attention:*`：`triage`、`design`、`blocked`；只表示需要關注的原因，不表示工作階段。
- `impact:*`：`breaking`、`migration`、`privacy`、`security`。

## 開發與驗證

- 服務生命週期一律由 Docker Compose 管理，不在宿主機直接啟動伺服器。
- 先建立會失敗的測試或明確重現步驟，再實作最小變更。
- 只修改需求需要的檔案，不重構無關程式碼。
- 優先執行受影響範圍的測試，再執行完整驗證。
- Pull Request 必須記錄實際執行的命令與結果。

## Pull Request 完成條件

- 連結原始 Issue；需要 RFC 時也連結已核准 RFC。
- 自動化測試通過，人工驗收情境附有證據。
- 使用者文件、設定範例與 migration 已同步。
- 相容性、安全與隱私影響已處理。
- 使用者可見變更已加入 `CHANGELOG.md` 的 `Unreleased`。
- 功能 item 只有進入正式 release 後才能移至 `Done`；RFC 文件 item 依 RFC 規範完成決策後可移至 `Done`。
```

- [ ] **Step 2: 建立 RFC 規範與範本**

建立 `docs/rfcs/README.md`：

```markdown
# Request for Comments（RFC）

RFC 用於在實作前記錄會影響多個模組、公開介面、資料、安全或長期維護成本的設計決策。

## RFC Decision

- `Pending`：尚未做出設計決策。
- `Accepted`：可拆分為實作 Issues 並移至 `Planned`。
- `Rejected`：不採用，文件保留理由。
- `Superseded`：已由另一份 RFC 取代。

RFC 不另建工作流程狀態。撰寫、審查與完成階段一律使用 GitHub Project 的 `Status`；`Decision` 只記錄設計決策結果。

## 流程

1. 建立 Feature Request 並完成 triage。
2. 複製本頁範本到 `docs/rfcs/NNNN-short-title.md`；`NNNN` 使用下一個四位數編號。
3. 在 RFC 與 Feature Request 互相連結。
4. RFC 完整後將 GitHub Project `Status` 改為 `Review`，`Decision` 保持 `Pending`。
5. 維護者記錄 `Accepted` 或 `Rejected` 決策及理由。
6. RFC 做出 `Accepted`、`Rejected` 或 `Superseded` 決策並記錄理由後，RFC 文件 item 移至 `Done`。
7. `Accepted` RFC 拆分實作 Issues；對應功能 item 仍須正式發布後才能移至 `Done`，發布後補上 release 連結。

## 範本

```markdown
# RFC NNNN：標題

- Decision: Pending
- Feature Request: #issue
- Authors: @username

## 問題

描述受影響使用者、目前行為與需要解決的限制。

## 目標

- 列出可驗證的預期成果。

## 非目標

- 列出本 RFC 明確不處理的範圍。

## 提案

描述元件邊界、公開介面、資料流與主要行為。

## 替代方案

列出考慮過的方案、優缺點與未採用理由。

## 資料與相容性

描述 schema、migration、向後相容性與資料保留影響；沒有影響時明確寫「無」。

## 安全與隱私

描述敏感資料、權限、威脅與緩解方式；沒有新增風險時說明判斷依據。

## 錯誤與復原

描述失敗模式、重試、回滾與使用者可見錯誤。

## 測試與驗收

列出自動化測試、端到端情境與完成條件。

## 發布與回滾

描述漸進發布、migration 順序、監控與回滾步驟。

## 決策

核准或拒絕時，由維護者記錄日期、結果與理由。
```

RFC 不可保留未定義的章節或用「之後處理」取代風險分析；不適用的章節必須明確寫出理由。
```

- [ ] **Step 3: 建立安全政策**

建立 `SECURITY.md`：

```markdown
# 安全政策

## 私下回報安全漏洞

請勿透過公開 Issue、Discussion、Pull Request 或日誌回報尚未修補的安全漏洞，也不要附上 API key、token、履歷、語音內容或其他個人資料。

請使用 [GitHub Private Vulnerability Reporting](https://github.com/Anuise/pro-copilot/security/advisories/new) 私下提交報告。Repository 維護者必須在 GitHub 的 Security 設定中啟用 Private vulnerability reporting，才能接收此類報告。

報告請包含：

- 受影響版本或 commit。
- 漏洞類型、影響與可利用情境。
- 最小重現步驟或概念驗證，且移除所有真實敏感資料。
- 已知緩解方式或建議修正方向。

維護者確認報告後，會透過 private advisory 協調重現、修補與揭露。修補發布前，請勿公開漏洞細節。

## 公開回報

不涉及安全性的一般錯誤請使用 GitHub Bug Report。若不確定問題是否屬於安全漏洞，優先使用私下回報。
```

- [ ] **Step 4: 建立 Pull Request 範本**

建立 `.github/pull_request_template.md`：

```markdown
## 變更摘要

<!-- 說明解決的問題與最小必要變更。 -->

## 追蹤連結

- Closes #
- RFC：不適用 / `docs/rfcs/NNNN-short-title.md`
- Roadmap item：Issue／Project 連結或 Not linked

## 驗證證據

<!-- 列出實際執行的命令、結果，以及人工驗收步驟。 -->

```text
命令：
結果：
```

## 影響

- [ ] 無破壞性變更；若有，已說明 migration 與回滾方式。
- [ ] 無新增安全或隱私風險；若有，已記錄並處理。
- [ ] 未在日誌、截圖或測試資料中包含敏感資訊。

## 完成檢查

- [ ] 已連結原始 Issue。
- [ ] 需要 RFC 時，已連結核准的 RFC。
- [ ] 已新增或更新自動化測試。
- [ ] Issue 的人工驗收情境已有證據。
- [ ] 使用者文件與設定範例已同步，或確認不適用。
- [ ] 資料庫或資料格式變更包含 migration，或確認不適用。
- [ ] 使用者可見變更已加入 `CHANGELOG.md` 的 `Unreleased`，或確認不適用。
```

- [ ] **Step 5: 在 README 加入專案規劃入口**

在 `README.md` 的「目錄結構」之後、「授權」之前加入：

```markdown
## 專案規劃與貢獻

- [Roadmap](ROADMAP.md)：目前、下一步與長期產品方向。
- [貢獻指南](docs/CONTRIBUTING.md)：Issue、GitHub Project、開發與驗收流程。
- [RFC 規範](docs/rfcs/README.md)：大型或高風險功能的設計流程。
- [Changelog](CHANGELOG.md)：已發布與尚未發布的使用者可見變更。
- [安全政策](SECURITY.md)：私下回報尚未修補的安全漏洞。

新功能請透過 GitHub Feature Request 提出；提交前請先確認是否需要 RFC。
```

- [ ] **Step 6: 驗證跨文件術語與連結**

Run:

```powershell
$files = @('ROADMAP.md', 'docs/CONTRIBUTING.md')
$requiredTerms = @('Now', 'Next', 'Later')
foreach ($file in $files) {
    $content = Get-Content -Raw $file
    foreach ($term in $requiredTerms) {
        if (-not $content.Contains($term)) { throw "$file 缺少術語 $term" }
    }
}
$pullRequestTemplate = Get-Content -Raw .github/pull_request_template.md
if (-not $pullRequestTemplate.Contains('Roadmap item：Issue／Project 連結或 Not linked')) {
    throw 'Pull Request 範本缺少 Roadmap item 連結欄位'
}
$links = @('ROADMAP.md', 'docs/CONTRIBUTING.md', 'docs/rfcs/README.md', 'CHANGELOG.md', 'SECURITY.md')
foreach ($link in $links) {
    if (-not (Test-Path $link)) { throw "README 連結目標不存在: $link" }
}
```

Expected: 命令無輸出並以 exit code `0` 結束。

- [ ] **Step 7: 執行完整文件驗證**

Run:

```powershell
$placeholderPattern = @('T' + 'BD', 'T' + 'ODO', '待定', '之後處理', 'fill ' + 'in', 'implement ' + 'later') -join '|'
rg -n $placeholderPattern ROADMAP.md CHANGELOG.md SECURITY.md docs/CONTRIBUTING.md docs/rfcs/README.md .github
git diff --check -- README.md ROADMAP.md CHANGELOG.md SECURITY.md docs/CONTRIBUTING.md docs/rfcs/README.md .github
```

Expected: `rg` 找不到未解決佔位符；`git diff --check` 無 whitespace error。

- [ ] **Step 8: Commit**

```bash
git add README.md SECURITY.md docs/CONTRIBUTING.md docs/rfcs/README.md .github/pull_request_template.md
git commit -m "docs: define contribution and RFC workflow"
```

### Task 4: 最終一致性驗收

**Files:**
- Verify: `ROADMAP.md`
- Verify: `CHANGELOG.md`
- Verify: `.github/ISSUE_TEMPLATE/feature_request.yml`
- Verify: `.github/ISSUE_TEMPLATE/bug_report.yml`
- Verify: `.github/ISSUE_TEMPLATE/config.yml`
- Verify: `.github/pull_request_template.md`
- Verify: `docs/CONTRIBUTING.md`
- Verify: `docs/rfcs/README.md`
- Verify: `README.md`
- Verify: `SECURITY.md`

**Interfaces:**
- Consumes: Tasks 1–3 的所有文件與 metadata。
- Produces: 可交付、可由 GitHub 使用、術語一致的需求追蹤系統。

- [ ] **Step 1: 核對設計規格覆蓋**

Run:

```powershell
$expected = @(
  'README.md',
  'SECURITY.md',
  'ROADMAP.md',
  'CHANGELOG.md',
  '.github/ISSUE_TEMPLATE/feature_request.yml',
  '.github/ISSUE_TEMPLATE/bug_report.yml',
  '.github/ISSUE_TEMPLATE/config.yml',
  '.github/pull_request_template.md',
  'docs/CONTRIBUTING.md',
  'docs/rfcs/README.md'
)
$missing = $expected | Where-Object { -not (Test-Path $_) }
if ($missing) { throw "缺少交付檔案: $($missing -join ', ')" }
```

Expected: 命令無輸出並以 exit code `0` 結束。

- [ ] **Step 2: 核對狀態與時程名稱**

Run:

```powershell
$contributing = Get-Content -Raw docs/CONTRIBUTING.md
$statuses = @('Inbox', 'Triaged', 'Planned', 'In Progress', 'Review', 'Done')
$horizons = @('Now', 'Next', 'Later', 'Not Planned')
foreach ($value in $statuses + $horizons) {
    if (-not $contributing.Contains($value)) { throw "貢獻指南缺少 $value" }
}
```

Expected: 命令無輸出並以 exit code `0` 結束。

- [ ] **Step 3: 確認未修改產品程式碼或使用者技能資料**

Run: `git diff --name-only`

Expected: 本計畫新增或修改的檔案僅限 `README.md`、`ROADMAP.md`、`CHANGELOG.md`、`SECURITY.md`、`.github/**`、`docs/CONTRIBUTING.md`、`docs/rfcs/README.md`、設計規格與本計畫；既有 `vault/skills` 修改仍保留但不屬於本計畫差異。

- [ ] **Step 4: 最終差異檢查**

Run: `git diff --check`

Expected: 無本計畫新增的 whitespace error。若輸出只涉及執行前已存在的使用者修改，記錄後停止，不修改那些檔案。
