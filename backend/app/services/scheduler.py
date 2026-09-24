from apscheduler.schedulers.background import BackgroundScheduler

from app.database.database import SessionLocal
from app.models.package import Package

from app.services.monitor_service import check_package


scheduler = BackgroundScheduler()


def monitor_all_packages():

    db = SessionLocal()

    try:

        packages = db.query(Package).filter(
            Package.is_monitored == True
        ).all()

        print(
            f"\n[SCHEDULER] Checking "
            f"{len(packages)} monitored package(s)..."
        )

        for package in packages:

            check_package(package.name)

    except Exception as e:

        print(
            f"[SCHEDULER] Error: {e}"
        )

    finally:

        db.close()


def start_scheduler():

    scheduler.add_job(
        monitor_all_packages,
        "interval",
        minutes=1,
        id="npm_monitor",
        replace_existing=True
    )

    scheduler.start()

    print(
        "[SCHEDULER] NPM monitoring started."
    )
