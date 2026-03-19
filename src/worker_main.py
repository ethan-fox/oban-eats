import asyncio
import logging
import signal
from oban import Oban
from src.config.settings import get_settings
from src.config.logging import configure_logging

configure_logging()


logger = logging.getLogger(__name__)

async def main():
    """
    Worker service entry point.
    Starts Oban worker that polls queue and processes jobs.
    Creates its own Oban instance with queue configuration.
    """
    logger.info("Starting Oban worker service...")

    settings = get_settings()

    QUEUES = {"high_priority": 1, "low_priority": 1}

    pool = await Oban.create_pool(dsn=settings.database_url)
    oban = Oban(
        pool=pool,
        queues=QUEUES,
        lifeline={"interval": 15, "rescue_after": 60},
        metrics=True
    )

    await oban.start()

    # Create an event to signal shutdown
    shutdown_event = asyncio.Event()

    # Handle shutdown signals
    def handle_shutdown(sig, _frame):
        logger.info(f"Received signal {sig}, gracefully stopping worker...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        logger.info("Oban worker running. Press Ctrl+C to stop.")
        await shutdown_event.wait()
    finally:
        logger.info("Gracefully shutting down Oban...")
        # Now stop Oban completely, allows current jobs to finish
        await oban.stop()
        # Close the connection pool; Oban does not do this itself
        await pool.close()
        logger.debug("Oban worker service stopped.")


if __name__ == "__main__":
    asyncio.run(main())
