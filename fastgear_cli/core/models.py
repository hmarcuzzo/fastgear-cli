from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class ProjectInitConfig(BaseModel):
    base_dir: Path = Field(default_factory=Path.cwd)
    project_name: str = Field(..., min_length=1)
    project_title: str = Field(..., min_length=1)
    use_docker: bool = Field(default=True)

    @field_validator("project_name")
    @classmethod
    def no_spaces_at_ends(cls, v: str) -> str:
        return v.strip()

    @property
    def project_dir(self) -> Path:
        return self.base_dir / self.project_name
