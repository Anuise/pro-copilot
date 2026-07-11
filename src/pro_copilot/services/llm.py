import os
from google.antigravity import Agent, LocalAgentConfig


async def call_llm(
    system_prompt: str,
    user_prompt: str,
) -> str:
    """使用 Antigravity SDK 啟動 Agent 並回傳生成的文字內容。"""
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key or gemini_key == "placeholder":
        if "職涯分析" in system_prompt:
            return """## 程式開發
- 技能名稱: Python
  熟練度: 精通
  相關專案: Pro-Copilot
  具體貢獻: S: 建立職涯副駕駛系統。T: 整合多種 API 並進行 Docker 部署。A: 使用 Python/FastAPI 開發後端。R: 順利完成專案功能驗證。

## 系統部署
- 技能名稱: Docker
  熟練度: 熟練
  相關專案: Pro-Copilot
  具體貢獻: S: 需要容器化部署。T: 撰寫 Dockerfile。A: 配置 volume 掛載與環境變數注入。R: 縮短部署時間 50%。
"""
        elif "履歷撰寫" in system_prompt:
            return """# 杜偉宏 (Wei-Hung Tu) 的客製化履歷

## 個人簡介
擁有豐富 Python、FastAPI、Docker 經驗的軟體工程師，擅長 AI 系統整合。

## 技術技能
- 語言: Python, TypeScript
- 後端: FastAPI, Uvicorn
- 容器化: Docker, Docker Compose

## 工作經歷
- 軟體工程師，使用 Docker 與 FastAPI 開發職涯副駕駛。
"""
        else:
            return "這是測試環境的預設 LLM Mock 內容。"

    config = LocalAgentConfig(system_instructions=system_prompt)

    async with Agent(config) as agent:
        response = await agent.chat(user_prompt)

        content = ""
        async for token in response:
            content += token
        return content
