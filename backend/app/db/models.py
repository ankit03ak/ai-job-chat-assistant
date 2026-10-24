from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("job_id", name="uq_applications_job_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    job_title_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    company_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), default="simulated_applied", nullable=False)
    application_method: Mapped[str] = mapped_column(String(50), default="simulated", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
