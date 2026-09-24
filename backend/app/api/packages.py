import json
import logging

import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.package import Package
from app.models.release import Release
from app.services.npm_monitor import get_package, get_package_metadata, parse_datetime
from app.services.relevance_engine import calculate_relevance_score
from app.services.threat_service import analyze_release

router = APIRouter(prefix="/packages", tags=["Packages"])
logger = logging.getLogger("npmvector.api.packages")


@router.get("/ranking")
def package_ranking(db: Session = Depends(get_db)):
    packages = (
        db.query(Package)
        .filter(Package.is_monitored == True)
        .order_by(Package.relevance_score.desc(), Package.name.asc())
        .all()
    )

    return {
        "packages": [
            {
                "name": package.name,
                "version": package.latest_version,
                "downloads": package.downloads,
                "score": package.relevance_score,
                "relevance": package.relevance_score,
                "priority": package.priority,
                "threat_score": latest_release.threat_score if latest_release else 0,
                "threat_level": latest_release.threat_level if latest_release else "LOW",
            }
            for package in packages
            for latest_release in [
                db.query(Release)
                .filter(Release.package_id == package.id)
                .order_by(Release.detected_at.desc())
                .first()
            ]
        ]
    }


@router.get("/priority/{priority_level}")
def packages_by_priority(priority_level: str, db: Session = Depends(get_db)):
    priority = priority_level.upper()

    allowed = {"HIGH", "MEDIUM", "LOW"}
    if priority not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Priority must be one of: HIGH, MEDIUM, LOW"
        )

    packages = (
        db.query(Package)
        .filter(Package.priority == priority)
        .order_by(Package.relevance_score.desc(), Package.name.asc())
        .all()
    )

    return {
        "priority": priority,
        "count": len(packages),
        "packages": [
            {
                "name": package.name,
                "score": package.relevance_score,
                "priority": package.priority,
            }
            for package in packages
        ],
    }


@router.get("/{package_name}/summary")
def package_summary(package_name: str, db: Session = Depends(get_db)):
    package = db.query(Package).filter(Package.name == package_name).first()

    if package is None:
        raise HTTPException(status_code=404, detail=f"Package '{package_name}' not found")

    release_count = db.query(Release).filter(Release.package_id == package.id).count()

    return {
        "name": package.name,
        "latest_version": package.latest_version,
        "downloads": package.downloads,
        "dependents": package.dependents,
        "relevance_score": package.relevance_score,
        "priority": package.priority,
        "release_count": release_count,
        "is_monitored": package.is_monitored,
    }


@router.get("/{package_name}")
def monitor_package(package_name: str, db: Session = Depends(get_db)):
    try:
        data = get_package(package_name)
        metadata = get_package_metadata(data)

        package = db.query(Package).filter(Package.name == package_name).first()

        if package is None:
            package = Package(
                name=metadata["name"],
                description=metadata["description"],
                latest_version=metadata["latest_version"],
                created_at=parse_datetime(metadata.get("created_at")),
            )

            db.add(package)
            db.commit()
            db.refresh(package)

            release = Release(
                package_id=package.id,
                version=metadata["latest_version"],
                change_type="initial_release",
            )

            db.add(release)
            db.flush()
            analyze_release(release.id, db=db)
            db.commit()

            return {
                "status": "success",
                "change_detected": True,
                "change_type": "initial_package",
                "package": {
                    "id": package.id,
                    "name": package.name,
                    "latest_version": package.latest_version,
                },
            }

        if package.created_at is None and metadata.get("created_at"):
            package.created_at = parse_datetime(metadata["created_at"])

        previous_version = package.latest_version
        current_version = metadata["latest_version"]

        if previous_version != current_version:
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

            return {
                "status": "success",
                "change_detected": True,
                "change_type": "new_release",
                "previous_version": previous_version,
                "current_version": current_version,
            }

        package_detail = {
            "name": package.name,
            "latest_version": package.latest_version,
            "downloads": package.downloads,
            "dependents": package.dependents,
            "relevance_score": package.relevance_score,
            "priority": package.priority,
            "is_monitored": package.is_monitored,
        }

        return {
            "status": "success",
            "change_detected": False,
            "message": "No new release detected",
            "version": current_version,
            "package": package_detail,
        }

    except requests.HTTPError as error:
        db.rollback()
        status_code = error.response.status_code if error.response is not None else 502
        if status_code == 404:
            raise HTTPException(status_code=404, detail=f"Package '{package_name}' not found")
        logger.exception("Registry error while checking package %s", package_name)
        raise HTTPException(status_code=502, detail="npm registry unavailable")
    except requests.RequestException:
        db.rollback()
        logger.exception("Network error while checking package %s", package_name)
        raise HTTPException(status_code=502, detail="npm registry unavailable")
    except Exception:
        db.rollback()
        logger.exception("Unexpected error while checking package %s", package_name)
        raise HTTPException(status_code=500, detail="Unable to check package")


@router.get("/{package_name}/versions")
def package_versions(package_name: str):
    data = get_package(package_name)
    versions = list(data.get("versions", {}).keys())
    return {"package": package_name, "versions": versions}


@router.get("/{package_name}/threats")
def package_threats(package_name: str, db: Session = Depends(get_db)):
    package = db.query(Package).filter(Package.name == package_name).first()

    if package is None:
        raise HTTPException(status_code=404, detail=f"Package '{package_name}' not found")

    releases = (
        db.query(Release)
        .filter(Release.package_id == package.id)
        .order_by(Release.detected_at.desc())
        .all()
    )

    threat_releases = []
    for release in releases:
        try:
            security_flags = json.loads(release.security_flags or "[]")
        except json.JSONDecodeError:
            security_flags = []

        threat_releases.append({
            "version": release.version,
            "threat_score": release.threat_score,
            "threat_level": release.threat_level,
            "security_flags": security_flags,
        })

    return {
        "package": package.name,
        "releases": threat_releases,
    }


@router.get("/{package_name}/releases")
def package_releases(package_name: str, db: Session = Depends(get_db)):
    package = db.query(Package).filter(Package.name == package_name).first()

    if package is None:
        raise HTTPException(status_code=404, detail=f"Package '{package_name}' not found")

    releases = (
        db.query(Release)
        .filter(Release.package_id == package.id)
        .order_by(Release.detected_at.desc())
        .all()
    )

    return {
        "package": package.name,
        "total_releases": len(releases),
        "releases": [
            {
                "version": release.version,
                "previous_version": release.previous_version,
                "change_type": release.change_type,
                "detected_at": release.detected_at.isoformat() if release.detected_at else None,
                "published_at": release.published_at.isoformat() if release.published_at else None,
            }
            for release in releases
        ],
    }


@router.get("/{package_name}/explain")
def package_explainability(package_name: str, db: Session = Depends(get_db)):
    package = db.query(Package).filter(Package.name == package_name).first()

    if package is None:
        raise HTTPException(status_code=404, detail=f"Package '{package_name}' not found")

    downloads_score = 0
    if package.downloads >= 100_000_000:
        downloads_score = 40
    elif package.downloads >= 10_000_000:
        downloads_score = 35
    elif package.downloads >= 1_000_000:
        downloads_score = 30
    elif package.downloads >= 100_000:
        downloads_score = 20
    elif package.downloads >= 10_000:
        downloads_score = 10
    else:
        downloads_score = 5

    dependents_score = 0
    if package.dependents >= 10_000:
        dependents_score = 25
    elif package.dependents >= 1_000:
        dependents_score = 20
    elif package.dependents >= 100:
        dependents_score = 15
    elif package.dependents >= 10:
        dependents_score = 10
    else:
        dependents_score = 5

    age_score = 0
    if package.created_at:
        age_days = (__import__('datetime').datetime.utcnow() - package.created_at).days
        if age_days >= 365 * 5:
            age_score = 15
        elif age_days >= 365 * 2:
            age_score = 12
        elif age_days >= 365:
            age_score = 10
        elif age_days >= 180:
            age_score = 7
        else:
            age_score = 4
    else:
        age_score = 4

    release_count = db.query(Release).filter(Release.package_id == package.id).count()
    if release_count >= 100:
        release_score = 20
    elif release_count >= 50:
        release_score = 15
    elif release_count >= 20:
        release_score = 10
    elif release_count >= 5:
        release_score = 7
    else:
        release_score = 3

    score, priority = calculate_relevance_score(
        downloads=package.downloads or 0,
        dependents=package.dependents or 0,
        package_age_days=max((__import__('datetime').datetime.utcnow() - package.created_at).days, 0) if package.created_at else 0,
        release_count=release_count,
    )

    return {
        "name": package.name,
        "score": score,
        "priority": priority,
        "signals": {
            "downloads": downloads_score,
            "dependents": dependents_score,
            "age": age_score,
            "release_activity": release_score,
        },
    }
