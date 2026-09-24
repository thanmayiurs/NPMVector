import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.database.database import SessionLocal
from app.models.package import Package

from app.services.monitor_service import check_package


scheduler = BackgroundScheduler()
logger = logging.getLogger("npmvector.scheduler")


def monitor_all_packages():

    db = SessionLocal()

    try:

        packages = db.query(Package).filter(
            Package.is_monitored == True
        ).all()

        logger.info("Checking %s monitored package(s)...", len(packages))

        for package in packages:

            check_package(package.name)

    except Exception:
        logger.exception("Scheduler monitoring cycle failed")

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

    logger.info("NPM monitoring started.")
