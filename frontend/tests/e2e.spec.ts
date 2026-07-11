import { test, expect } from "@playwright/test";

test.describe("Pro-Copilot 全功能 E2E 測試", () => {
  test.beforeEach(async ({ page }) => {
    // 進入首頁
    await page.goto("/");
  });

  test("1. 驗證首頁載入與 Header 資訊", async ({ page }) => {
    // 檢查標題
    await expect(page.locator("header h1")).toHaveText("Pro-Copilot");
    await expect(page.locator("header p")).toHaveText("AI 職涯副駕駛");

    // 檢查後端狀態
    const statusText = page.locator("header span");
    await expect(statusText).toBeVisible();
    const currentStatus = await statusText.innerText();
    console.log(`目前系統連線狀態: ${currentStatus}`);
    expect(["系統連線中", "連線中..."]).toContain(currentStatus);
  });

  test("2. 驗證側邊欄導航切換", async ({ page }) => {
    // 切換至技能 Wiki 庫
    await page.click('nav button:has-text("技能 Wiki 庫")');
    await expect(page.locator('h2:has-text("技能 Wiki 庫")')).toBeVisible();

    // 切換至 RAG 履歷生成
    await page.click('nav button:has-text("RAG 履歷生成")');
    await expect(page.locator('h2:has-text("RAG 客製化履歷生成")')).toBeVisible();

    // 切換至系統同步日誌
    await page.click('nav button:has-text("系統同步日誌")');
    await expect(page.locator('h2:has-text("系統同步日誌")')).toBeVisible();

    // 切回主控制台
    await page.click('nav button:has-text("主控制台")');
    await expect(page.locator('span:has-text("RAG-Powered AI Copilot")')).toBeVisible();
  });

  test("3. 驗證同步向量資料庫按鈕運作 (Mocking API)", async ({ page }) => {
    // Mock 向量同步 API 的回覆以防 backend / Qdrant 連線等外部因素干擾
    await page.route("**/api/skills/sync-vector", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ synced_count: 5 }),
      });
    });

    // 點擊同步按鈕
    page.on("dialog", async (dialog) => {
      expect(dialog.message()).toContain("向量同步成功");
      await dialog.accept();
    });

    await page.click('button:has-text("同步向量資料庫")');
  });

  test("4. 驗證 RAG 履歷生成表單與 Mocking 生成結果", async ({ page }) => {
    // 切換至 RAG 履歷生成
    await page.click('nav button:has-text("RAG 履歷生成")');

    // 填寫表單
    await page.fill('input[placeholder*="Senior Python Backend Engineer"]', "測試職缺 - AI 工程師");
    await page.fill('textarea[placeholder*="請在此貼上目標職缺的 JD"]', "熟悉 Python, FastAPI, Docker, 與 LLM 整合開發。");

    // Mock 履歷生成 API 的回覆
    await page.route("**/api/cv/generate", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          cv: "# 測試產生的履歷\n\n- **Python**: 熟練運用於後端開發與測試。\n- **FastAPI**: 用於實作高效 API 服務。",
        }),
      });
    });

    // 點擊生成按鈕
    await page.click('button:has-text("開始 RAG 履歷優化與生成")');

    // 驗證產生的履歷預覽
    await expect(page.locator('h1:has-text("測試產生的履歷")')).toBeVisible();
    await expect(page.locator('strong:has-text("Python")')).toBeVisible();
  });
});
