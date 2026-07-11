# 手動蒸餾工作足跡功能實作計畫 (Manual Distillation Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在前端「技能 Wiki 庫」右上角新增一個「手動蒸餾工作足跡」綠色按鈕，點擊後觸發後端 API 執行每週蒸餾，並在完成後彈窗提示重整技能庫。

**Architecture:** 
1. 後端 `src/pro_copilot/api/skills.py` 新增 `POST /api/skills/distill` 端點。
2. 前端 `frontend/src/app/page.tsx` 新增 `distilling` 載入狀態、`handleDistillData` 異步 API 呼叫函式，並在 UI 排版中將該按鈕放置於「重新同步向量庫」的左側。

**Tech Stack:** FastAPI, Next.js (React), Tailwind CSS, Lucide React (Cpu icon).

## Global Constraints
- 一律使用繁體中文進行溝通與 UI 文字。
- 按鈕必須包含 Lucide 的 `Cpu` 圖示，並在蒸餾時旋轉。
- 點擊後按鈕需變為禁用 (disabled) 狀態以防重複點擊。

---

### Task 1: 後端新增手動蒸餾 API 端點

**Files:**
- Modify: `src/pro_copilot/api/skills.py`

**Interfaces:**
- Consumes: `pro_copilot.services.distiller.run_weekly_distillation`
- Produces: `POST /api/skills/distill` 回傳 `{"status": "success", "message": "每週蒸餾執行成功"}`

- [ ] **Step 1: 修改後端技能路由檔案**
  
  修改 [skills.py](file:///E:/program/pro-copilot/src/pro_copilot/api/skills.py)，在檔案頂部引入 `run_weekly_distillation`（如果尚未引入），並在檔案末尾新增 `distill` 的 POST 端點。

  在 [skills.py](file:///E:/program/pro-copilot/src/pro_copilot/api/skills.py) 新增的程式碼：
  ```python
  @router.post("/distill")
  async def trigger_distill():
      """手動觸發每週蒸餾服務。"""
      from pro_copilot.services.distiller import run_weekly_distillation
      try:
          await run_weekly_distillation()
          return {"status": "success", "message": "每週蒸餾執行成功"}
      except Exception as exc:
          logger.error("手動執行每週蒸餾失敗: %s", exc)
          raise HTTPException(status_code=500, detail=f"蒸餾執行失敗: {exc}")
  ```

- [ ] **Step 2: 驗證後端 API 編譯無誤**

  執行編譯驗證命令：
  ```bash
  .venv\Scripts\python -m py_compile src/pro_copilot/api/skills.py
  ```
  預期輸出：無任何錯誤輸出。

- [ ] **Step 3: 提交後端變更**

  ```bash
  git add src/pro_copilot/api/skills.py
  git commit -m "feat(api): add POST /api/skills/distill endpoint"
  ```

---

### Task 2: 前端新增手動蒸餾按鈕與事件處理

**Files:**
- Modify: `frontend/src/app/page.tsx`

**Interfaces:**
- Consumes: `POST /api/skills/distill` API

- [ ] **Step 1: 新增前端狀態與請求處理函式**

  修改 [page.tsx](file:///E:/program/pro-copilot/frontend/src/app/page.tsx)：
  1. 確保從 `lucide-react` 引入了 `Cpu` 圖示：
     ```typescript
     import { ... RefreshCw, Cpu ... } from "lucide-react";
     ```
  2. 在 `App` 元件內新增 `distilling` 狀態變數：
     ```typescript
     const [distilling, setDistilling] = useState(false);
     ```
  3. 新增 `handleDistillData` 處理函式：
     ```typescript
     const handleDistillData = async () => {
       setDistilling(true);
       try {
         const res = await fetch(`${API_BASE}/api/skills/distill`, { method: "POST" });
         if (res.ok) {
           alert("🎉 技能蒸餾成功！已成功分析最新日誌並更新 Wiki 庫。");
           fetchData();
         } else {
           const errData = await res.json().catch(() => ({}));
           alert(`❌ 蒸餾失敗: ${errData.detail || "請檢查後端日誌。"}`);
         }
       } catch (err) {
         alert("❌ 無法連線至後端 API。");
       } finally {
         setDistilling(false);
       }
     };
     ```

- [ ] **Step 2: 在 UI 技能分頁新增按鈕**

  在 [page.tsx](file:///E:/program/pro-copilot/frontend/src/app/page.tsx) 約 536 行附近的技能 Wiki 庫頁首處，將原本的按鈕外層包裝改為 flex 排版，並在左側放入「手動蒸餾工作足跡」按鈕：

  ```tsx
  {/* 原按鈕修改為 flex-row 的按鈕群組 */}
  <div className="flex space-x-3">
    <button
      onClick={handleDistillData}
      disabled={distilling}
      className="flex items-center space-x-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 text-xs px-3.5 py-2 rounded-xl transition-all"
    >
      <Cpu className={`h-3.5 w-3.5 ${distilling ? "animate-spin" : ""}`} />
      <span>{distilling ? "蒸餾中..." : "手動蒸餾工作足跡"}</span>
    </button>
    <button
      onClick={handleSyncVector}
      disabled={syncingVector}
      className="flex items-center space-x-2 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 hover:bg-indigo-500/20 text-xs px-3.5 py-2 rounded-xl transition-all"
    >
      <RefreshCw className={`h-3.5 w-3.5 ${syncingVector ? "animate-spin" : ""}`} />
      <span>{syncingVector ? "同步中..." : "重新同步向量庫"}</span>
    </button>
  </div>
  ```

- [ ] **Step 3: 提交前端變更**

  ```bash
  git add frontend/src/app/page.tsx
  git commit -m "feat(frontend): add manual distillation button next to sync vector"
  ```
