from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.database.database import Base


class Package(Base):

    __tablename__ = "packages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    latest_version = Column(
        String,
        nullable=True
    )

    downloads = Column(
        Integer,
        default=0
    )

    dependents = Column(
        Integer,
        default=0
    )

    is_monitored = Column(
        Boolean,
        default=True,
        nullable=False
    )

    relevance_score = Column(
        Integer,
        default=0,
        nullable=False
    )

    priority = Column(
        String,
        default="LOW",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )