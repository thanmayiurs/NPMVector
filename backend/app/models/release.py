from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime

from app.database.database import Base


class Release(Base):

    __tablename__ = "releases"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    package_id = Column(
        Integer,
        ForeignKey("packages.id"),
        nullable=False
    )

    version = Column(
        String,
        nullable=False
    )

    previous_version = Column(
        String,
        nullable=True
    )

    published_at = Column(
        DateTime,
        nullable=True
    )

    detected_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    tarball_url = Column(
        String,
        nullable=True
    )

    change_type = Column(
        String,
        default="new_release"
    )

    threat_score = Column(
        Integer,
        default=0,
        nullable=False
    )

    threat_level = Column(
        String,
        default="LOW",
        nullable=False
    )

    security_flags = Column(
        Text,
        nullable=True
    )