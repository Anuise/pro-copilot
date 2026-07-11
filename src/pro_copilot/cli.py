import asyncio
from pathlib import Path

import click


@click.group()
def main():
    """Pro-Copilot — 個人職涯副駕駛 CLI 工具。"""


@main.command()
def init():
    """初始化職涯帳本（Career Ledger）。"""
    from pro_copilot.services.bootstrap import run_bootstrap

    click.echo("⏳ 正在初始化職涯帳本…")
    asyncio.run(run_bootstrap())
    click.echo("✅ 初始化完成。")


@main.command()
@click.option("--jd", required=True, type=click.Path(exists=True), help="職缺描述檔路徑")
def generate(jd: str):
    """根據職缺描述生成客製化履歷。"""
    from pro_copilot.services.cv_generator import generate_cv

    jd_path = Path(jd)
    click.echo(f"⏳ 正在根據 {jd_path.name} 生成履歷…")
    asyncio.run(generate_cv(jd_path))
    click.echo("✅ 履歷生成完成。")


@main.command()
def distill():
    """手動觸發每週蒸餾。"""
    from pro_copilot.services.distiller import run_weekly_distillation

    click.echo("⏳ 正在執行每週蒸餾…")
    asyncio.run(run_weekly_distillation())
    click.echo("✅ 每週蒸餾完成。")


@main.command()
def convert():
    """手動將 raw_logs/incoming/ 下的 Office/PDF 文件轉換為 Markdown。"""
    from pro_copilot.services.document_converter import run_document_conversion

    click.echo("⏳ 正在執行文件格式轉換…")
    asyncio.run(run_document_conversion())
    click.echo("✅ 文件轉換完成。")


if __name__ == "__main__":
    main()
