import asyncio
import logging
from oban import Oban
from src.config.settings import get_settings

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def main():
    """
    Worker service entry point.
    Starts Oban worker that polls queue and processes jobs.
    Creates its own Oban instance with queue configuration.
    """
    logging.info("Starting Oban worker service...")

    settings = get_settings()

    oban = Oban(
        pool=Oban.create_pool(dsn=settings.database_url),
        queues={"high_priority": 5, "low_priority": 10}
    )

    await oban.start()

    logging.info("Oban worker service stopped.")


if __name__ == "__main__":
    asyncio.run(main())
