from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Profile(
    TimestampMixin,
    Base,
):
    __tablename__ = "profiles"

    user_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    username: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    total_xp: Mapped[int] = mapped_column(
        default=0,
        server_default="0",
        nullable=False,
    )

    current_level: Mapped[int] = mapped_column(
        default=1,
        server_default="1",
        nullable=False,
    )

    current_streak: Mapped[int] = mapped_column(
        default=0,
        server_default="0",
        nullable=False,
    )

    longest_streak: Mapped[int] = mapped_column(
        default=0,
        server_default="0",
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="profile",
        lazy="joined",
    )

    __table_args__ = (
        CheckConstraint(
            "char_length(username) >= 3",
            name="username_min_length",
        ),
        CheckConstraint(
            "total_xp >= 0",
            name="total_xp_non_negative",
        ),
        CheckConstraint(
            "current_level >= 1",
            name="current_level_positive",
        ),
        CheckConstraint(
            "current_streak >= 0",
            name="current_streak_non_negative",
        ),
        CheckConstraint(
            "longest_streak >= current_streak",
            name="longest_streak_valid",
        ),
    )

    def __repr__(self) -> str:
        return f"Profile(user_id={self.user_id!r}, username={self.username!r})"
