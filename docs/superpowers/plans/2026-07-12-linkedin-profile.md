# LinkedIn 個人檔案模擬功能實施計劃

本計劃概述了新增 LinkedIn 個人檔案模擬與手動複製功能的具體實施步驟，以確保開發工作的精準度與可驗證性。

## 1. 實施步驟與驗證點

### 步驟 1: 建立預設 LinkedIn 個人資料 JSON 檔
* **任務**：在 `vault/linkedin_profile.json` 建立一個包含預設 Fullstack / AI 開發者經歷的 JSON 檔案。
* **驗證**：確保檔案存在且為合法的 JSON。

### 步驟 2: 後端 Pydantic 模型與 API 路由開發
* **任務**：
  * 在 `src/pro_copilot/api/linkedin.py` 中，定義 Pydantic 模型 `LinkedInProfile` 與其內嵌結構 `Experience`、`Education`。
  * 實作 `GET /api/linkedin`：讀取 `vault/linkedin_profile.json`，如果不存在則先複製預設值；然後讀取 `vault/skills/` 的所有技能 Markdown 卡片，並整合回傳。
  * 實作 `PUT /api/linkedin`：接受前端的編輯內容，並儲存回 `vault/linkedin_profile.json`。
* **驗證**：在 `src/pro_copilot/main.py` 中註冊此 router。

### 步驟 3: 撰寫後端單元測試
* **任務**：建立 `tests/api/test_linkedin.py` 測試，對 API 進行 Mock 或整合測試，驗證讀寫行為。
* **驗證**：執行 pytest 或 unittest，測試全部通過。

### 步驟 4: 前端頁面開發 (Next.js)
* **任務**：
  * 修改 `frontend/src/app/page.tsx`，在 Tab 選項中加入 `linkedin`。
  * 實作 LinkedIn 風格的渲染介面：包含頂部 Banner、大頭貼圈、姓名、Headline、地區、About 區塊、工作經歷區塊、動態技能區塊。
  * 實作各區塊一鍵複製到剪貼簿功能。
  * 實作編輯模式，提供使用者在網頁上編輯基本資料與經歷列表，並打 API 保存。
* **驗證**：用 `npm run build` 進行 Next.js 的編譯測試，確認前端沒有 TypeScript 編譯錯誤。

### 步驟 5: 啟動服務與視覺化驗證
* **任務**：
  * 使用 `docker compose up -d --build` 啟動所有容器（包含 frontend 與 app）。
  * 執行 Playwright 測試或手動調用 Playwright 檢查前端 `linkedin` Tab 能否正確載入、點擊編輯、複製文字。
* **驗證**：驗證通過。

---

## 2. 影響範圍
* 新增檔案：
  * `vault/linkedin_profile.json` (預設資料)
  * `src/pro_copilot/api/linkedin.py` (API 路由)
  * `tests/api/test_linkedin.py` (後端測試)
* 修改檔案：
  * `src/pro_copilot/main.py` (註冊路由)
  * `frontend/src/app/page.tsx` (前端 UI)
