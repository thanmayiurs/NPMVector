import json
from datetime import datetime, timedelta

from app.database.database import SessionLocal
from app.models.package import Package
from app.models.release import Release
from app.services.npm_monitor import get_package
from app.services.package_analyzer import (
    analyze_package_json,
    compare_dependencies,
)
from app.services.security_engine import (
    calculate_threat_score,
    get_threat_level,
)


def _maintainer_names(version_data):
    return sorted(
        maintainer.get("name") or maintainer.get("email")
        for maintainer in version_data.get("maintainers", [])
        if maintainer.get("name") or maintainer.get("email")
    )


def _version_data(package_data, version):
    if not version:
        return {}
    return package_data.get("versions", {}).get(version, {})


def get_investigation_priority(relevance_score, threat_level):
    high_relevance = (relevance_score or 0) >= 70
    high_threat = threat_level == "HIGH"

    if high_relevance and high_threat:
        return "IMMEDIATE INVESTIGATION"
    if high_threat:
        return "INVESTIGATE"
    if high_relevance:
        return "MONITOR"
    return "LOW PRIORITY"


def analyze_release(release_id, db=None):
    owns_session = db is None
    session = db or SessionLocal()

    try:
        release = session.query(Release).filter(Release.id == release_id).first()
        if release is None:
            raise ValueError(f"Release not found: {release_id}")

        package = session.query(Package).filter(
            Package.id == release.package_id
        ).first()
        if package is None:
            raise ValueError(f"Package not found for release: {release_id}")

        package_data = get_package(package.name)
        current_data = _version_data(package_data, release.version)
        previous_data = _version_data(package_data, release.previous_version)
        flags = analyze_package_json({
            "dist-tags": {"latest": release.version},
            "versions": {release.version: current_data},
        })

        previous_dependencies = previous_data.get("dependencies", {})
        current_dependencies = current_data.get("dependencies", {})
        dependency_changes = compare_dependencies(
            previous_dependencies,
            current_dependencies,
        )

        if dependency_changes["added"]:
            flags.append({
                "type": "new_dependency",
                "packages": dependency_changes["added"],
            })

        dependency_count_increased = len(current_dependencies) > len(previous_dependencies)
        if dependency_count_increased:
            flags.append({
                "type": "dependency_count_increased",
                "from": len(previous_dependencies),
                "to": len(current_dependencies),
            })

        maintainer_changed = False
        package_size_increased = False
        if release.previous_version:
            current_maintainers = _maintainer_names(current_data)
            previous_maintainers = _maintainer_names(previous_data)
            maintainer_changed = current_maintainers != previous_maintainers
            if maintainer_changed:
                flags.append({
                    "type": "maintainer_changed",
                    "from": previous_maintainers,
                    "to": current_maintainers,
                })

            previous_size = previous_data.get("dist", {}).get("unpackedSize", 0)
            current_size = current_data.get("dist", {}).get("unpackedSize", 0)
            package_size_increased = current_size > previous_size
            if package_size_increased:
                flags.append({
                    "type": "package_size_increased",
                    "from": previous_size,
                    "to": current_size,
                })

        recent_release_count = session.query(Release).filter(
            Release.package_id == package.id,
            Release.detected_at >= datetime.utcnow() - timedelta(hours=1),
        ).count()
        unusual_release = recent_release_count >= 3
        if unusual_release:
            flags.append({
                "type": "unusual_release",
                "releases_last_hour": recent_release_count,
            })

        score, _ = calculate_threat_score(
            has_install_script=any(flag["type"] == "install_script" for flag in flags),
            has_new_dependency=bool(dependency_changes["added"]),
            dependency_count_increased=dependency_count_increased,
            unusual_release=unusual_release,
            maintainer_changed=maintainer_changed,
            package_size_increased=package_size_increased,
        )

        release.threat_score = score
        release.threat_level = get_threat_level(score)
        release.security_flags = json.dumps(flags)

        if owns_session:
            session.commit()
        else:
            session.flush()

        return {
            "release_id": release.id,
            "threat_score": release.threat_score,
            "threat_level": release.threat_level,
            "security_flags": flags,
        }
    except Exception:
        if owns_session:
            session.rollback()
        raise
    finally:
        if owns_session:
            session.close()
