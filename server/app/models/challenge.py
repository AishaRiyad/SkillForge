from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ChallengeStatus

if TYPE_CHECKING:
    from app.models.lesson import Lesson
    from app.models.question import Question


class Challenge(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "challenges"

    lesson_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "lessons.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    passing_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=70,
        server_default="70",
    )

    xp_reward: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
        server_default="100",
    )

    max_attempts: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[ChallengeStatus] = mapped_column(
        Enum(
            ChallengeStatus,
            name="challenge_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=ChallengeStatus.DRAFT,
        server_default=ChallengeStatus.DRAFT.value,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    lesson: Mapped["Lesson"] = relationship(
        back_populates="challenges",
    )

    questions: Mapped[list["Question"]] = relationship(
        back_populates="challenge",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Question.position",
    )
