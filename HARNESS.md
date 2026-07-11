# 通用 AI 開發 Harness

本文件是所有 AI 開發工具的單一工作入口。供應商專屬指令可以補充操作方式，但不得降低本文件、`AGENTS.md` 或使用者需求的限制。

## 讀取順序

1. 使用者當前需求。
2. 變更檔案適用範圍內的 `AGENTS.md`。
3. 本文件。
4. 與工作相關的 README、RFC、規格及原始碼。

發生衝突時依上述順序採用較高優先級規則，並在工作狀態的 `requirements.assumptions` 記錄決策。

## 啟動工作

每項非微小工作使用獨立狀態檔。檔名可對應 Issue 或工作識別碼，但不得包含空白、憑證或個人資料。

```bash
docker compose run --rm --no-deps app uv run python scripts/harness.py init .harness/task.json
```

狀態格式由 [`.harness/schema.json`](.harness/schema.json) 定義，[`.harness/task.example.json`](.harness/task.example.json) 提供最小範例。狀態檔是執行證據，不取代 GitHub Project；正式需求的生命週期仍以 GitHub Project `Status` 為唯一來源。

## 標準循環

階段只能依序前進：

`intake → design → plan → implement → verify → review → done`

每次切換階段都要依序附加至 `phase_history`，驗證器會拒絕跳關或倒退。任何未完成階段都可附加 `blocked`；解除阻塞後必須附加原本尚未完成的階段，並在 `open_items` 記錄阻塞原因與需要的外部條件。

### 1. intake

- 原樣保留需求於 `requirements.request`。
- 列出假設、限制、明確非目標與可檢查的成功條件。
- 先檢查工作區與既有變更，不覆蓋不屬於本工作的內容。

### 2. design

- 先讀現有實作與文件，再選擇最小方案。
- 在 `design.alternatives` 記錄考慮過的替代方案及捨棄理由。
- 在 `design.risks` 記錄相容性、安全、隱私、資料與回滾風險。
- 符合 `docs/CONTRIBUTING.md` 條件時，核准 RFC 前不得實作。

### 3. plan

- `plan` 每一項都必須是可驗證的成果，不是模糊活動。
- 行為變更採測試先行：先建立會因缺少目標行為而失敗的測試，再實作最小修正。
- 計畫必須指出受影響範圍與驗證方式。

### 4. implement

- 只修改可直接追溯到需求的檔案與行數。
- 不順手重構、重新格式化或修復無關問題。
- 發現需求外問題時寫入 `open_items`，不得擴大工作範圍。

### 5. verify

- 先執行最小受影響測試，再執行合理範圍的完整驗證。
- 服務、API 與 E2E 目標一律由 Docker Compose 啟動，不在宿主機啟動伺服器。
- 每次實際執行結果依時間順序附加至 `verification`，只允許 `pass`、`fail`、`not_run`；不得把預期結果記為實際證據。
- 失敗時不得進入 `review`，應修正根因或轉為 `blocked`。

### 6. review

- 對照原始需求、成功條件、diff 與驗證輸出進行自審。
- 檢查遺漏需求、不必要變更、敏感資料、相容性與文件同步。
- 只有實際審查通過才能設定 `review.status` 為 `pass`。

### 7. done

只有下列條件全部成立才能宣告完成：

- 成功條件非空且逐項有對應成果。
- 計畫、變更檔案與變更摘要已記錄。
- 至少一筆實際驗證結果為 `pass`。
- `review.status` 為 `pass`。
- `open_items` 為空。
- harness 檢查命令成功。

```bash
docker compose run --rm --no-deps app uv run python scripts/harness.py check .harness/task.json
```

## 不可接受的捷徑

- 未讀規則或現有程式碼便直接修改。
- 以「應該可行」取代實際測試輸出。
- 刪除、重設或覆蓋既有工作區變更。
- 在狀態檔、輸出、測試資料或提交內容中放入 secret 或個人資料。
- 為通過檢查而偽造命令、結果、審查或清空仍存在的問題。

## 驗證 Harness 本身

```bash
docker compose run --rm --no-deps --build app uv run python -m unittest tests.test_harness -v
```

驗證器只讀取狀態檔並檢查證據，不會執行其中記錄的命令。
