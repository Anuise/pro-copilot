# 語言規則 (Language Rule)

- 一律使用繁體中文進行溝通與回覆。

---

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. 運行與測試環境規則 (Environment & Testing Rules)

**一律在 Docker Compose 容器內運行服務，嚴禁在宿主機直接啟動伺服器：**

- **嚴禁在宿主機（Host）上執行**：像是 `uvicorn`、`next dev`、`npm run dev`、`python main.py` 等會佔用埠口（如 3000, 8000）的伺服器啟動命令。
- **統一使用 Docker Compose 進行生命週期管理**：
  - 啟動與重新啟動伺服器：請使用 `docker compose up -d` 或 `docker compose restart [service_name]`。
  - 重建並啟動服務：`docker compose up -d --build [service_name]`。
  - 停止服務：`docker compose down`。
- **測試環境依賴**：任何端對端測試（如 Playwright E2E 測試）或 API 驗證，其對應的伺服器（Target Server）必須是由 Docker 容器所運行的實例，而非宿主機啟動的本機實例。

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
