from enum import StrEnum


class EnvironmentOption(StrEnum):
    PRODUCTION = "production"
    QA = "qa"
    DEVELOPMENT = "development"
    LOCAL = "local"
