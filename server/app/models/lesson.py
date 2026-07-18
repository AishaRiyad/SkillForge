from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import LessonStatus

if TYPE_CHECKING:
    from app.models.course import Course


class Lesson(
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "lessons"

    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "position",
            name="uq_lessons_course_position",
        ),
        UniqueConstraint(
            "course_id",
            "slug",
            name="uq_lessons_course_slug",
        ),
    )

    course_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "courses.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(180),
        nullable=False,
        index=True,
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    video_url: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
    )

    estimated_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    is_preview: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    status: Mapped[LessonStatus] = mapped_column(
        Enum(
            LessonStatus,
            name="lesson_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=LessonStatus.DRAFT,
        server_default=LessonStatus.DRAFT.value,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    course: Mapped["Course"] = relationship(
        back_populates="lessons",
    )

    def __repr__(self) -> str:
        return (
            f"Lesson(id={self.id!r}, title={self.title!r}, position={self.position!r})"
        )
