# 貢獻指南

感謝你協助改進 Pro-Copilot。本專案同時處理個人工作紀錄、AI 產出與外部服務整合，因此所有變更都必須可追溯、可測試，且不得暴露敏感資料。

## 開始之前

- 錯誤請使用 Bug Report。
- 新功能或行為變更請使用 Feature Request。
- 不要在公開 Issue、Pull Request 或日誌貼上 API key、token、履歷內容、語音內容或其他個人資料。
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
- 只有進入正式 release 後，Project item 才能移至 `Done`。
