import logging

from fastgear.utils import LoggerUtils as FastgearLoggerUtils
from src.core.constants.enums import EnvironmentOption


class LoggerUtils:
    @staticmethod
    def configure_logging(environment: EnvironmentOption) -> None:
        FastgearLoggerUtils.configure_logging(LoggerUtils.get_log_level(environment))

    @staticmethod
    def get_log_level(environment: EnvironmentOption) -> int:
        log_levels = {
            EnvironmentOption.PRODUCTION: logging.WARNING,
            EnvironmentOption.QA: logging.INFO,
            EnvironmentOption.DEVELOPMENT: logging.DEBUG,
            EnvironmentOption.LOCAL: logging.DEBUG,
        }

        return log_levels.get(environment, logging.DEBUG)
