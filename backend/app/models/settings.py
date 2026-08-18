import uuid

from sqlalchemy import Boolean, Enum, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import ApiProviderType
from app.models.mixins import TimestampMixin, UUIDPkMixin


class ApiProvider(Base, UUIDPkMixin):
    __tablename__ = "api_providers"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    type: Mapped[ApiProviderType] = mapped_column(
        Enum(
            ApiProviderType,
            native_enum=False,
            create_constraint=False,
            validate_strings=True,
            values_callable=lambda e: [member.value for member in e],
        )
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[dict] = mapped_column(JSONB, default=dict)


class Setting(Base, UUIDPkMixin):
    __tablename__ = "settings"
    __table_args__ = (UniqueConstraint("key"),)

    key: Mapped[str] = mapped_column(String(100))
    value: Mapped[dict] = mapped_column(JSONB)


class AuditLog(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "audit_logs"

    action: Mapped[str] = mapped_column(String(100))
    entity_type: Mapped[str] = mapped_column(String(100))
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    log_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
