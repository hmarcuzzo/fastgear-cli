import re
from pathlib import Path

import typer
from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import ValidationInfo

from fastgear_cli.cli.commands.helpers.add_controller_helper import (
    ask_service_path,
)
from fastgear_cli.cli.commands.helpers.add_controller_helper import (
    validate_service_path as validate_controller_service_path,
)
from fastgear_cli.cli.commands.helpers.add_repository_helper import (
    ask_entity_path,
)
from fastgear_cli.cli.commands.helpers.add_repository_helper import (
    validate_entity_path as validate_repository_entity_path,
)
from fastgear_cli.cli.commands.helpers.add_service_helper import (
    ask_repository_path,
)
from fastgear_cli.cli.commands.helpers.add_service_helper import (
    validate_repository_path as validate_service_repository_path,
)
from fastgear_cli.core.constants.enums import ElementTypeEnum


class AddElementConfig(BaseModel):
    base_dir: Path = Field(default_factory=Path.cwd)
    element_type: ElementTypeEnum | str = Field(default=None)
    element_name: str = Field(..., min_length=1)
    use_folders: bool = Field(default=True)
    entity_path: str | None = Field(default=None, validate_default=True)
    repository_path: str | None = Field(default=None, validate_default=True)
    service_path: str | None = Field(default=None, validate_default=True)

    @field_validator("base_dir", mode="before")
    @classmethod
    def normalize_base_dir(cls, v: str | None) -> Path:
        return Path.cwd() if v is None else Path(v)

    @field_validator("element_type", mode="before")
    @classmethod
    def convert_element_type(cls, v: str) -> ElementTypeEnum:
        try:
            return ElementTypeEnum(v.strip().lower())
        except ValueError:
            typer.secho(
                "Invalid element type. Use one of: module | controller | service | entity | repository",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)

    @field_validator("element_name", mode="before")
    @classmethod
    def normalize_element_name(cls, v: str) -> str:
        v = v.strip()

        v = v.replace("-", "_").replace(" ", "_")
        v = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", v)
        v = re.sub(r"[^a-zA-Z0-9_]", "", v)
        v = re.sub(r"_+", "_", v).strip("_").lower()

        if not v:
            typer.secho(
                "Element name must contain letters or numbers.",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)

        return v

    @field_validator("entity_path", mode="after")
    @classmethod
    def validate_entity_path(cls, v: str | None, info: ValidationInfo) -> str | None:
        if info.data.get("element_type") != ElementTypeEnum.REPOSITORY:
            return v

        if v is None:
            return ask_entity_path()

        return validate_repository_entity_path(v)

    @field_validator("repository_path", mode="after")
    @classmethod
    def validate_repository_path(cls, v: str | None, info: ValidationInfo) -> str | None:
        if info.data.get("element_type") != ElementTypeEnum.SERVICE:
            return v

        if v is None:
            return ask_repository_path()

        return validate_service_repository_path(v)

    @field_validator("service_path", mode="after")
    @classmethod
    def validate_service_path(cls, v: str | None, info: ValidationInfo) -> str | None:
        if info.data.get("element_type") != ElementTypeEnum.CONTROLLER:
            return v

        if v is None:
            return ask_service_path()

        return validate_controller_service_path(v)

    @property
    def structure(self) -> str:
        return "folder" if self.use_folders else "flat"

    @property
    def context(self) -> dict:
        context = {
            "element_name": self.element_name,
            "element_class_name": "".join(
                part.capitalize() for part in self.element_name.split("_") if part
            ),
        }

        if self.entity_path:
            import_path = self.entity_path.rsplit(".", 1)[0]
            class_name = self.entity_path.rsplit(".", 1)[1]
            context.update(
                {
                    "entity_import_path": import_path,
                    "entity_class_name": class_name,
                }
            )

        if self.repository_path:
            import_path = self.repository_path.rsplit(".", 1)[0]
            class_name = self.repository_path.rsplit(".", 1)[1]
            context.update(
                {
                    "repository_import_path": import_path,
                    "repository_class_name": class_name,
                }
            )

        if self.service_path:
            import_path = self.service_path.rsplit(".", 1)[0]
            class_name = self.service_path.rsplit(".", 1)[1]
            context.update(
                {
                    "service_import_path": import_path,
                    "service_class_name": class_name,
                }
            )

        return context
