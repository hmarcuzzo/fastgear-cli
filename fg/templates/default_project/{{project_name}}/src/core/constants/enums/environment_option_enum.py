from enum import StrEnum


class EnvironmentOption(StrEnum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    QA = "qa"
    PRODUCTION = "production"
