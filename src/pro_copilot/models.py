from datetime import datetime, timezone
from sqlalchemy import Text, DateTime, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from pro_copilot.database import Base

class CVHistory(Base):
    __tablename__ = "cv_histories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    jd_title: Mapped[str] = mapped_column(String(255), nullable=False)
    jd_content: Mapped[str] = mapped_column(Text, nullable=False)
    generated_cv: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

class SyncLog(Base):
    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # gitlab, calendar, voice
    status: Mapped[str] = mapped_column(String(50), nullable=False)       # success, failed
    detail: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
