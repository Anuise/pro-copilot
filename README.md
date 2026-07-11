# Pro-Copilot — AI 職涯副駕駛

> 自動蒸餾工作足跡為 Obsidian 技能 wiki 並生成客製履歷

## 快速開始（Docker Compose）

```bash
# 1. 複製環境變數範本
cp .env.example .env

# 2. 填入你的 API 金鑰
#    編輯 .env，設定 OPENAI_API_KEY（Whisper 語音轉文字）等

# 3. 啟動服務
docker compose up --build
```

服務啟動後，API 預設在 `http://localhost:8000` 上運行。

## 開發環境（uv）

```bash
# 安裝依賴
uv sync

# 啟動開發伺服器（自動重載）
uv run uvicorn pro_copilot.main:app --reload
```

## CLI 指令

```bash
# 初始化職涯帳本（從 init/ 目錄載入歷史資料）
uv run pro-copilot init

# 根據目標職缺 JD 生成客製履歷
uv run pro-copilot generate --jd ./jobs/target-JD.md

# 手動將 raw_logs/incoming/ 底下的 Office/PDF 文件轉換成 Markdown
uv run pro-copilot convert

# 手動執行每週蒸餾（會自動先呼叫 convert 轉換新文件，再進行 AI 分析）
uv run pro-copilot distill
```

## 目錄結構

```
pro-copilot/
├── src/pro_copilot/        # Python 套件原始碼
│   ├── api/                # FastAPI 路由
│   └── services/           # 商業邏輯
├── raw_logs/               # 原始工作日誌（Git 忽略）
│   ├── incoming/           # 待轉換的原始 Office (docx/pptx/xlsx) 與 PDF 文件
│   │   └── archive/        # 轉換成功後自動移入的封存區
│   ├── documents/          # Office/PDF 轉換出的 Markdown 檔案
│   ├── gitlab/             # GitLab webhook 資料
│   ├── calendar/           # Google Calendar 事件
│   └── voice/              # Telegram 語音轉文字
├── init/                   # 初始化用歷史資料
├── vault/                  # Obsidian 知識庫
│   ├── skills/             # 技能 wiki 頁面
│   └── daily/              # 每日摘要
├── jobs/                   # 目標職缺 JD
├── pyproject.toml          # 專案設定與依賴
├── Dockerfile              # 容器映像檔定義
├── docker-compose.yml      # Docker Compose 設定
└── .env.example            # 環境變數範本
```

## 授權

詳見 [LICENSE](LICENSE) 檔案。
