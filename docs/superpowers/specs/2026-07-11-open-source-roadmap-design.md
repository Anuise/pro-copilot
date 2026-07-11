# Pro-Copilot 開源 Roadmap 與需求追蹤設計

## 目標

將 Pro-Copilot 發展為可公開發布的開源產品，同時服務：

- 希望透過 Docker Compose 自行部署的個人使用者。
- 希望理解、修改或擴充資料來源與 AI 流程的開發者。

第一個公開版本維持單人自架模式，不納入帳號、多租戶、雲端託管或付費機制。Roadmap 不承諾固定日期，使用 `Now / Next / Later` 與可驗證的完成條件管理進度。

## 現況摘要

目前核心價值流程為：

1. 從 GitLab、Google Calendar、Telegram 語音與 Office/PDF 文件蒐集工作足跡。
2. 透過 LLM 將足跡蒸餾為 Obsidian 技能 Wiki。
3. 將技能內容同步到 Qdrant。
4. 根據職缺描述檢索相關技能並生成客製履歷。
5. 透過 Next.js 介面查看技能、日誌與履歷歷史。

現有功能已形成可操作原型，但公開發布前仍需建立可重現部署、自動化測試、設定驗證、安全邊界、資料遷移、貢獻流程與端到端驗收基線。

## Roadmap 組織原則

採用「風險優先、使用者旅程驗收」：

- 先消除會阻止陌生使用者安裝、驗證與信任系統的風險。
- 再完善「資料輸入 → 技能蒸餾 → 履歷輸出」的第一次成功旅程。
- 最後建立穩定的擴充介面與社群貢獻生態。
- `ROADMAP.md` 只呈現產品主題、成果與完成條件；具體工作由 GitHub Issues 與 GitHub Project 追蹤。

## Now：可信賴的開源基線

### 目標

陌生使用者能依文件完成部署，開發者能安全修改並驗證變更。

### 範圍

- 修正 README 與專案 Docker Compose 執行規則的衝突。
- 建立後端單元與整合測試、前端 E2E 測試基線。
- 建立 GitHub Actions，執行 lint、測試、映像建置與 Compose smoke test。
- 啟動時驗證必要環境變數，避免 mock 或靜默降級被誤認為正式結果。
- 保護 webhook、檔案上傳、憑證與 API 錯誤訊息。
- 建立可重現的資料庫 schema migration 流程。
- 提供範例資料，以及不需真實付費 API 金鑰的 smoke test。
- 建立貢獻指南、Issue 與 PR 範本、RFC 規範及 changelog。

### 完成條件

- 全新環境可只依 README 使用 Docker Compose 啟動所有必要服務。
- CI 可驗證 lint、測試、建置與基礎服務健康狀態。
- smoke test 不依賴真實付費 API，失敗時能指出缺少的設定或服務。
- 敏感設定不會出現在版本庫、一般 API 回應或預設日誌中。

## Next：第一次成功旅程

### 目標

非開發者可透過 Web UI 完成「資料輸入 → 技能蒸餾 → 履歷輸出」。

### 範圍

- 建立首次設定與外部服務連線檢查頁。
- 顯示各資料來源的同步狀態、最近成功時間及可操作錯誤。
- 支援蒸餾預覽與人工確認後寫入，避免 AI 直接覆寫知識庫。
- 改善技能去重、來源引用、更新歷史與可追溯性。
- 提供 JD 匯入、履歷版本比較及標準格式匯出。
- 顯示長時間任務進度，提供失敗重試與安全復原。
- 建立備份、還原及個人資料匯出流程。
- 發布第一個穩定版本與完整操作教學。

### 完成條件

- 新使用者不需執行應用程式 CLI，即可透過 Web UI 完成核心旅程。
- 每份技能更新可追溯到來源紀錄與確認動作。
- 每份生成履歷可追溯到使用的職缺描述與技能來源。
- 備份資料可在乾淨環境中成功還原並通過核心旅程驗證。

## Later：擴充與社群生態

### 目標

外部貢獻者能新增資料來源或 AI provider，而不需修改核心流程。

### 範圍

- 定義資料來源 adapter 或 plugin 介面。
- 增加 GitHub、Notion、Jira 等資料來源。
- 支援替換 LLM 與 embedding provider。
- 建立技能 schema、匯入匯出格式及相容性版本規則。
- 提供外掛範例、開發文件與貢獻者測試工具。
- 建立文件網站、範例展示及社群治理規則。
- 評估桌面封裝、離線模型與多人模式；評估不代表承諾實作。

## 暫不納入

- 登入與帳號管理。
- 多使用者協作與租戶隔離。
- 官方雲端託管服務。
- 付費、訂閱與帳務。
- 原生行動 App。

上述項目若未來重新評估，必須先提出功能需求並通過 RFC 流程，不因列於 `Later` 而自動取得實作承諾。

## 追蹤架構

採用「文件定方向、GitHub 管執行」的雙層架構：

1. `ROADMAP.md` 定義產品方向、階段成果與完成條件。
2. GitHub Feature Request 收集新功能想法與驗收情境。
3. Triage 確認價值、範圍、風險、重複性及產品方向。
4. 大型或高風險功能先建立 RFC；小型功能可直接規劃。
5. GitHub Project 管理工作狀態與 `Now / Next / Later / Not Planned` 時程。
6. 實作 Issue、Pull Request、測試、文件及 changelog 保持互相連結。
7. 功能發布後才標記 `Done`，並同步 roadmap 的階段狀態。

## GitHub Project 欄位

### Status

- `Inbox`：尚未完成分流。
- `Triaged`：問題與範圍已確認，尚未承諾排程。
- `Planned`：已核准並具有驗收條件。
- `In Progress`：已有負責人且正在實作。
- `Review`：程式、文件或驗收正在審查。
- `Done`：已發布且所有完成條件已滿足。

### Horizon

- `Now`：目前優先完成的成果。
- `Next`：Now 完成後的候選成果。
- `Later`：方向一致但尚未承諾的長期候選。
- `Not Planned`：目前不符合方向或成本效益，保留決策理由。

`Status` 描述工作所處階段，`Horizon` 描述產品優先時程，兩者不可互相取代。

## 功能需求最低資訊

每個 Feature Request 必須描述：

- 要解決的問題與受影響使用者。
- 目前替代方式及其不足。
- 預期成果與可觀察的成功條件。
- 明確不處理的範圍。
- 隱私、安全、資料遷移與相容性影響。
- 可由維護者重現的驗收情境。

隱私、安全、資料遷移與相容性影響必須逐項填寫「有／無／不確定」及理由，不可用未勾選的選項取代分析。缺少問題描述、驗收條件或影響分析的需求維持在 `Inbox`，不進入 `Planned`。

## RFC 適用條件

符合任一條件即需 RFC：

- 同時修改前端與後端的主要使用流程。
- 改變資料格式、資料庫 schema、技能 schema 或公開介面。
- 引入新的基礎設施、長期運行服務或外部依賴。
- 涉及破壞性變更、安全模型、隱私或資料遷移。
- 建立供後續外掛或第三方整合依賴的擴充介面。

RFC 至少包含問題、目標、非目標、方案、替代方案、資料流、安全與隱私、遷移、測試、發布及回滾方式。RFC 使用 `Decision: Pending / Accepted / Rejected / Superseded` 記錄設計決策，不另建工作流程狀態；撰寫與審查階段沿用 GitHub Project `Status`。RFC 核准前不得將對應功能移至 `Planned`。

RFC 文件 item 與功能 item 分開收尾：RFC 做出 `Accepted`、`Rejected` 或 `Superseded` 決策並記錄理由後即可移至 `Done`；對應功能 item 仍須在正式發布後才能移至 `Done`。

## Labels

固定使用以下 label namespace：

- `type:*`：`feature`、`bug`、`docs`、`maintenance`、`security`。
- `area:*`：`frontend`、`api`、`ai`、`ingestion`、`storage`、`devops`、`docs`。
- `priority:*`：`critical`、`high`、`medium`、`low`。
- `attention:*`：`triage`、`design`、`blocked`。
- `impact:*`：`breaking`、`migration`、`privacy`、`security`。

GitHub Project 的 `Status` 是唯一工作流程狀態來源；`attention:*` 只表示需要關注的原因，不表示工作所處階段。其他 labels 只補充查詢與風險資訊，避免重複維護兩套狀態。

## 完成定義

功能只有在以下條件全部滿足後才能關閉：

- Pull Request 連結原始 Issue；若適用，也連結已核准 RFC。
- 自動化測試通過，且 Issue 中的人工驗收情境已有證據。
- 使用者文件、設定範例與 migration 已同步更新。
- 相容性、安全與隱私影響已處理。
- 使用者可見變更已加入 changelog。
- 變更已包含在正式 release；release 前最多只能處於 `Review`。

## 預計建立的專案檔案

- `ROADMAP.md`：產品方向、階段內容與完成條件。
- `.github/ISSUE_TEMPLATE/feature_request.yml`：結構化功能需求。
- `.github/ISSUE_TEMPLATE/bug_report.yml`：結構化錯誤回報。
- `.github/ISSUE_TEMPLATE/config.yml`：Issue template 選擇設定。
- `.github/pull_request_template.md`：Issue、測試、文件與發布檢查。
- `SECURITY.md`：GitHub Private Vulnerability Reporting 私下回報政策。
- `docs/CONTRIBUTING.md`：分流、優先級、Project 與開發流程。
- `docs/rfcs/README.md`：RFC 適用條件、決策值與範本。
- `CHANGELOG.md`：依版本記錄已發布變更。

## 驗證方式

- YAML 範本可由 GitHub Issue Forms 正確解析。
- Feature Request 含有本設計要求的所有最低資訊。
- Pull Request 範本涵蓋完成定義。
- `ROADMAP.md`、貢獻指南與 RFC 文件使用一致的 Project 狀態、時程、RFC 決策值與 label 名稱。
- 全部文件不包含未定義縮寫、未解決佔位符或日期承諾。
- 安全漏洞回報連結指向 `https://github.com/Anuise/pro-copilot/security/advisories/new`，且 repository 需啟用 Private vulnerability reporting。
