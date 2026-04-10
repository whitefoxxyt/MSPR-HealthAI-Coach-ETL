import os
import signal
import sys
import threading

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from main import run_pipeline
from pipelines import PIPELINES
from utils.logger import get_logger

logger = get_logger("scheduler")

CRON_SCHEDULE = os.environ.get("CRON_SCHEDULE", "0 2 * * *")  # Chaque jour à 2h
SHUTDOWN_TIMEOUT = int(os.environ.get("SHUTDOWN_TIMEOUT", "600"))  # 10 minutes


def run_all_pipelines():
    logger.info("Démarrage des pipelines ETL (schedulé)")
    for pipeline in PIPELINES:
        run_pipeline(pipeline)
    logger.info("Tous les pipelines ETL terminés")


def main():
    logger.info("Scheduler ETL démarré — schedule : %s", CRON_SCHEDULE)

    # Exécution immédiate au démarrage
    run_all_pipelines()

    # Planification récurrente
    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_all_pipelines,
        CronTrigger.from_crontab(CRON_SCHEDULE),
        id="etl_pipelines",
        misfire_grace_time=3600,  # Tolère 1h de retard avant de sauter
    )

    def shutdown(signum, frame):
        logger.info(
            "Signal reçu (%s), arrêt propre en cours (timeout: %ds)...", signum, SHUTDOWN_TIMEOUT
        )
        t = threading.Thread(target=lambda: scheduler.shutdown(wait=True), daemon=True)
        t.start()
        t.join(timeout=SHUTDOWN_TIMEOUT)
        if t.is_alive():
            logger.warning("Timeout d'arrêt dépassé (%ds), arrêt forcé.", SHUTDOWN_TIMEOUT)
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler arrêté.")


if __name__ == "__main__":
    main()
