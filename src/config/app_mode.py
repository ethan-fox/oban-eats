"""Application deployment modes."""
from enum import Enum


class AppMode(str, Enum):
    """
    Deployment modes for the application.
    Determines which components are active.
    """
    API = "api"
    WORKER = "worker"
