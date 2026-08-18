import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import SearchJobStatus
from app.models.mixins import TimestampMixin, UUIDPkMixin


class SearchJob(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "search_jobs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE")
    )
    params: Mapped[dict] = mapped_column(JSONB)
    status: Mapped[SearchJobStatus] = mapped_column(
        Enum(
            SearchJobStatus,
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            values_callable=lambda e: [member.value for member in e],
        ),
        default=SearchJobStatus.PENDING,
    )
    found_count: Mapped[int] = mapped_column(Integer, default=0)
    processed_count: Mapped[int] = mapped_column(Integer, default=0)
    checked_count: Mapped[int] = mapped_column(Integer, default=0)
    qualified_count: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    results: Mapped[list["SearchResult"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class SearchResult(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "search_results"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("search_jobs.id", ondelete="CASCADE")
    )
    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE")
    )
    raw_provider_payload: Mapped[dict] = mapped_column(JSONB)

    job: Mapped["SearchJob"] = relationship(back_populates="results")


class SavedSearch(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "saved_searches"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(255))
    params: Mapped[dict] = mapped_column(JSONB)
