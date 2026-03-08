import re
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from fastgear_cli.core.constants.enums import ElementTypeEnum
from fastgear_cli.core.exceptions import InvalidInputError


def parse_element_type(value: str) -> ElementTypeEnum:
    try:
        return ElementTypeEnum(value.strip().lower())
    except ValueError as error:
        raise InvalidInputError(
            "Invalid element type. Use one of: module | controller | service | entity | repository"
        ) from error


def normalize_element_name(value: str) -> str:
    normalized = value.strip()
    normalized = normalized.replace("-", "_").replace(" ", "_")
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized)
    normalized = re.sub(r"[^a-zA-Z0-9_]", "", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_").lower()

    if not normalized:
        raise InvalidInputError("Element name must contain letters or numbers.")

    return normalized


class AddElementConfig(BaseModel):
    base_dir: Path = Field(default_factory=Path.cwd)
    element_type: ElementTypeEnum
    element_name: str = Field(..., min_length=1)
    use_folders: bool = Field(default=True)
    entity_path: str | None = Field(default=None)
    repository_path: str | None = Field(default=None)
    service_path: str | None = Field(default=None)

    @field_validator("base_dir", mode="before")
    @classmethod
    def normalize_base_dir(cls, v: str | None) -> Path:
        return Path.cwd() if v is None else Path(v)

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
