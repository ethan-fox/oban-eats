import logging


def configure_logging(log_level: str = "INFO") -> None:
    """
    Shared logging configuration for both API and Worker services.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="[%(levelname)s] %(asctime)s#%(name)s: %(message)s"
    )
