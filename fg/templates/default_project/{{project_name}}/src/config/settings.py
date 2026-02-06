from enum import StrEnum
from pathlib import Path
from typing import Annotated

from fastgear.types.base_settings import TomlBaseSettings
from pydantic import Field, StringConstraints
from pydantic_settings import SettingsConfigDict

from src.core.constants.enums import EnvironmentOption

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = Path(ROOT_DIR, "config", "toml")


def _get_toml_files(config_dir: Path, env_enum: type[StrEnum]) -> list[str]:
    candidates: list[Path] = [
        config_dir / "env.toml",
        config_dir / "env.local.toml",
    ]

    for env in env_enum:
        candidates.append(config_dir / f"env.{env.value}.toml")
        candidates.append(config_dir / f"env.{env.value}.local.toml")

    seen: set[Path] = set()
    files: list[str] = []
    for p in candidates:
        if not p.exists():
            continue
        if p in seen:
            continue
        seen.add(p)
        files.append(str(p))

    return files


class AppSettings(TomlBaseSettings):
    APP_ENV: EnvironmentOption = EnvironmentOption.DEVELOPMENT
    APP_TZ: Annotated[str, StringConstraints()] = "UTC"
    APP_PORT: Annotated[int, Field(default=8000, ge=1, le=65535)]

    CORS_ORIGINS: list[Annotated[str, StringConstraints(min_length=1)]] = ["*"]

    IS_PRODUCTION: bool = APP_ENV == EnvironmentOption.PRODUCTION

    model_config = SettingsConfigDict(
        toml_file=_get_toml_files(CONFIG_DIR, EnvironmentOption), extra="ignore"
    )


class Settings(AppSettings):
    model_config = SettingsConfigDict(
        toml_file=AppSettings.model_config["toml_file"],
        extra="ignore",
        validate_default=True,
    )


settings = Settings()
