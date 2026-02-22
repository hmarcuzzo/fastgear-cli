import re
from pathlib import Path

import typer
from pydantic import BaseModel, Field, field_validator

from fastgear_cli.core.constants.enums import ElementTypeEnum


class AddElementConfig(BaseModel):
    base_dir: Path = Field(default_factory=Path.cwd)
    element_type: ElementTypeEnum | str = Field(default=None)
    element_name: str = Field(..., min_length=1)
    use_folders: bool = Field(default=True)

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

    @property
    def structure(self) -> str:
        return "folder" if self.use_folders else "flat"

    @property
    def context(self) -> dict:
        return {
            "element_name": self.element_name,
            "element_class_name": "".join(
                part.capitalize() for part in self.element_name.split("_") if part
            ),
        }
