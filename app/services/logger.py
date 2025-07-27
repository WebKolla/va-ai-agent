""" Logger module for the application """

import os
from abc import ABC, abstractmethod


class Logger(ABC):
    """Logger interface"""

    @abstractmethod
    def info(self, message: str) -> None:
        pass

    @abstractmethod
    def error(self, message: str) -> None:
        pass


class ConsoleLogger(Logger):
    """Console logger class"""

    def info(self, message: str) -> None:
        print(f"INFO: {message}")

    def error(self, message: str) -> None:
        print(f"ERROR: {message}")


class LogfireLogger(Logger):
    """Logfire logger class"""

    def __init__(self):

        try:
            import logfire

            logfire.configure()
            logfire.instrument_pydantic_ai()
            self.logfire = logfire
            self.available = True
        except Exception as e:
            print(f"Logfire initialization failed: {e}")
            self.fallback = ConsoleLogger()

    def info(self, message: str) -> None:
        if self.available:
            self.logfire.info(message)
        else:
            self.fallback.info(message)

    def error(self, message: str) -> None:
        if self.available:
            self.logfire.error(message)
        else:
            self.fallback.error(message)


def get_logger() -> Logger:
    """Get logger based on environment config."""
    if os.getenv("LOGFIRE_ENABLED", "false").lower() == "true":
        return LogfireLogger()

    return ConsoleLogger()
