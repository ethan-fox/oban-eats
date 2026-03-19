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

    oban = Oban(
        pool=await Oban.create_pool(dsn=settings.database_url),
        queues={"high_priority": 5, "low_priority": 10},
        lifeline={"interval": 15, "rescue_after": 60},
        metrics=True
    )

    await oban.start()

    # Create an event to signal shutdown
    shutdown_event = asyncio.Event()

    # Handle shutdown signals
    def handle_shutdown(sig, frame):
        logger.info(f"Received signal {sig}, gracefully stopping worker...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        logger.info("Oban worker running. Press Ctrl+C to stop.")
        await shutdown_event.wait()
    finally:
        logger.info("Shutting down Oban...")
        await oban.stop()
        logger.info("Oban worker service stopped.")


if __name__ == "__main__":
    asyncio.run(main())
