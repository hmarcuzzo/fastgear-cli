from pathlib import Path
from typing import Annotated

from fastgear.types.base_settings import TomlBaseSettings
from pydantic import Field, StringConstraints
from pydantic_settings import SettingsConfigDict

from src.core.constants.enums import EnvironmentOption

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = Path(ROOT_DIR, "config", "toml")


def _get_toml_files(config_dir, enviroment_options) -> list[str]:
    base_file = Path(config_dir, "env.toml")
    development_file = Path(config_dir, "env.development.toml")
    local_file = Path(config_dir, "env.local.toml")

    files = [str(base_file)]

    if development_file.exists():
        files.append(str(development_file))

    if local_file.exists():
        files.append(str(local_file))

    return files


class AppSettings(TomlBaseSettings):
    APP_ENV: EnvironmentOption = EnvironmentOption.DEVELOPMENT
    APP_TZ: Annotated[str, StringConstraints()] = "UTC"
    APP_PORT: Annotated[int, Field(default=8000, ge=1, le=65535)]

    CORS_ORIGINS: list[Annotated[str, StringConstraints(min_length=1)]] = ["*"]

    IS_PRODUCTION: bool = APP_ENV == EnvironmentOption.PRODUCTION

    model_config = SettingsConfigDict(toml_file=_get_toml_files(CONFIG_DIR, None), extra="ignore")


class Settings(AppSettings):
    model_config = SettingsConfigDict(
        toml_file=AppSettings.model_config["toml_file"],
        extra="ignore",
        validate_default=True,
    )


settings = Settings()
