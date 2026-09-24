from datetime import datetime

from app.database.database import SessionLocal
from app.models.package import Package
from app.models.release import Release

from app.services.relevance_engine import calculate_relevance_score


def calculate_package_relevance(package_name: str):

    db = SessionLocal()

    try:

        # Find package
        package = db.query(Package).filter(
            Package.name == package_name
        ).first()

        if package is None:
            print(f"[RELEVANCE] Package not found: {package_name}")
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

        print(
            f"[RELEVANCE] {package_name} "
            f"Score={score} "
            f"Priority={priority}"
        )

        return {
            "package": package_name,
            "score": score,
            "priority": priority
        }

    except Exception as e:

        db.rollback()

        print(
            f"[RELEVANCE] Error for "
            f"{package_name}: {e}"
        )

    finally:

        db.close()
