from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.package import Package
from app.models.release import Release

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def dashboard_stats(db: Session = Depends(get_db)):
    total_packages = db.query(Package).count()
    monitored_packages = db.query(Package).filter(
        Package.is_monitored == True
    ).count()

    high_priority = db.query(Package).filter(
        Package.priority == "HIGH"
    ).count()
    medium_priority = db.query(Package).filter(
        Package.priority == "MEDIUM"
    ).count()
    low_priority = db.query(Package).filter(
        Package.priority == "LOW"
    ).count()

    total_releases = db.query(Release).count()
    high_threats = db.query(Release).filter(
        Release.threat_level == "HIGH"
    ).count()
    medium_threats = db.query(Release).filter(
        Release.threat_level == "MEDIUM"
    ).count()
    low_threats = db.query(Release).filter(
        Release.threat_level == "LOW"
    ).count()

    return {
        "packages": {
            "total": total_packages,
            "monitored": monitored_packages,
        },
        "priority": {
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority,
        },
        "releases": {
            "total": total_releases,
        },
        "threats": {
            "high": high_threats,
            "medium": medium_threats,
            "low": low_threats,
        },
    }


@router.get("/releases")
def dashboard_releases(db: Session = Depends(get_db)):
    rows = (
        db.query(Release, Package)
        .join(Package, Release.package_id == Package.id)
        .order_by(Release.detected_at.desc())
        .limit(8)
        .all()
    )

    return {
        "releases": [
            {
                "package": package.name,
                "previous_version": release.previous_version,
                "version": release.version,
                "threat_score": release.threat_score,
                "threat_level": release.threat_level,
                "detected_at": release.detected_at.isoformat() if release.detected_at else None,
            }
            for release, package in rows
        ]
    }