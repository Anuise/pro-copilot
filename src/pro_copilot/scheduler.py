from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from pro_copilot.services.distiller import run_weekly_distillation

_scheduler: AsyncIOScheduler | None = None


def start_scheduler():
    """啟動排程器：每週六 09:00 執行每週蒸餾。"""
    global _scheduler
    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        run_weekly_distillation,
        trigger=CronTrigger(day_of_week="sat", hour=9, minute=0),
        id="weekly_distillation",
        name="每週蒸餾",
        replace_existing=True,
    )
    _scheduler.start()


def stop_scheduler():
    """關閉排程器。"""
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
