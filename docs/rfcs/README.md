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
6. `Accepted` RFC 拆分實作 Issues；功能發布後補上 release 連結。

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
