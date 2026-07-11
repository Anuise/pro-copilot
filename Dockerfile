# syntax=docker/dockerfile:1
FROM python:3.14-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# 先複製依賴描述檔，利用 Docker layer cache
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# 複製原始碼並安裝專案
COPY . .
RUN uv sync --frozen --no-dev

# 建立資料目錄
RUN mkdir -p \
    raw_logs/gitlab \
    raw_logs/calendar \
    raw_logs/voice \
    init \
    vault/skills \
    vault/daily \
    jobs

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "pro_copilot.main:app", "--host", "0.0.0.0", "--port", "8000"]
