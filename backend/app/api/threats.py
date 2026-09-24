from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.package import Package
from app.models.release import Release
from app.services.threat_service import get_investigation_priority

router = APIRouter(prefix="/threats", tags=["Threats"])


@router.get("/high")
def high_threats(db: Session = Depends(get_db)):
    rows = (
        db.query(Release, Package)
        .join(Package, Release.package_id == Package.id)
        .filter(Release.threat_level == "HIGH")
        .order_by(Release.threat_score.desc(), Release.detected_at.desc())
        .all()
    )

    threats = [
        {
            "package": package.name,
            "version": release.version,
            "threat_score": release.threat_score,
            "threat_level": release.threat_level,
            "relevance_score": package.relevance_score,
            "investigation_priority": get_investigation_priority(
                package.relevance_score,
                release.threat_level,
            ),
        }
        for release, package in rows
    ]

    return {
        "count": len(threats),
        "threats": threats,
    }