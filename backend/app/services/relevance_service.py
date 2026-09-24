from datetime import datetime
import logging

from app.database.database import SessionLocal
from app.models.package import Package
from app.models.release import Release

from app.services.relevance_engine import calculate_relevance_score

logger = logging.getLogger("npmvector.relevance")


def calculate_package_relevance(package_name: str):

    db = SessionLocal()

    try:

        # Find package
        package = db.query(Package).filter(
            Package.name == package_name
        ).first()

        if package is None:
            logger.warning("Package not found: %s", package_name)
            return

        # --------------------------------
        # 1. Downloads
        # --------------------------------
        downloads = package.downloads or 0

        # --------------------------------
        # 2. Dependents
        # --------------------------------
        dependents = package.dependents or 0

        # --------------------------------
        # 3. Package age
        # --------------------------------
        if package.created_at:
            age = datetime.utcnow() - package.created_at
            package_age_days = age.days
        else:
            package_age_days = 0

        # --------------------------------
        # 4. Release count
        # --------------------------------
        release_count = db.query(Release).filter(
            Release.package_id == package.id
        ).count()

        # --------------------------------
        # Calculate score
        # --------------------------------
        score, priority = calculate_relevance_score(
            downloads=downloads,
            dependents=dependents,
            package_age_days=package_age_days,
            release_count=release_count
        )

        # --------------------------------
        # Save to database
        # --------------------------------
        package.relevance_score = score
        package.priority = priority

        db.commit()

        logger.info(
            "%s Score=%s Priority=%s",
            package_name,
            score,
            priority,
        )

        return {
            "package": package_name,
            "score": score,
            "priority": priority
        }

    except Exception:

        db.rollback()

        logger.exception("Error calculating relevance for %s", package_name)

    finally:

        db.close()
