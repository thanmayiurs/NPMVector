import logging

from app.database.database import SessionLocal
from app.models.package import Package
from app.models.release import Release
from app.services.npm_monitor import (
    get_downloads,
    get_package,
    get_package_metadata,
)
from app.services.relevance_service import calculate_package_relevance
from app.services.threat_service import analyze_release

logger = logging.getLogger("npmvector.monitor")


def is_new_release(previous_version, current_version):
    return bool(current_version and current_version != previous_version)


def check_package(package_name: str):
    db = SessionLocal()

    try:
        package = db.query(Package).filter(
            Package.name == package_name
        ).first()

        if package is None:
            logger.warning("Package not found: %s", package_name)
            return

        if not package.is_monitored:
            logger.info("Skipping disabled package: %s", package_name)
            return

        data = get_package(package_name)
        metadata = get_package_metadata(data)
        downloads = get_downloads(package_name)
        package.downloads = downloads

        current_version = metadata["latest_version"]
        previous_version = package.latest_version

        if is_new_release(previous_version, current_version):
            release = Release(
                package_id=package.id,
                version=current_version,
                previous_version=previous_version,
                change_type="new_release",
            )
            db.add(release)
            db.flush()
            analyze_release(release.id, db=db)
            package.latest_version = current_version
            db.commit()
            logger.info(
                "New release detected: %s %s -> %s",
                package_name,
                previous_version,
                current_version,
            )
        else:
            db.commit()
            calculate_package_relevance(package_name)
            logger.info(
                "No change: %s@%s | Downloads: %s",
                package_name,
                current_version,
                downloads,
            )

    except Exception:
        db.rollback()
        logger.exception("Error checking package %s", package_name)
    finally:
        db.close()
