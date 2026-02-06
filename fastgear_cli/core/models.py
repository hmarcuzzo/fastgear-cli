from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class ProjectInitConfig(BaseModel):
    name: str = Field(..., min_length=1)

    @field_validator("name")
    @classmethod
    def no_spaces_at_ends(cls, v: str) -> str:
        return v.strip()

    @property
    def project_dir(self) -> Path:
        return Path(self.name)
