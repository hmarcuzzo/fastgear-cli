from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from fastgear_cli.core.constants.enums import (
    AgentToolsEnum,
    CIProviderEnum,
    DatabaseProviderEnum,
)


class ProjectInitConfig(BaseModel):
    base_dir: Path = Field(default_factory=Path.cwd)
    project_name: str = Field(..., min_length=1)
    project_title: str = Field(..., min_length=1)
    use_docker: bool = Field(default=True)
    agent_tools: list[AgentToolsEnum | str] = Field(default_factory=list)
    ci_provider: CIProviderEnum | str | None = Field(default=None)
    use_database: bool = Field(default=False)
    database_provider: DatabaseProviderEnum | str | None = Field(default=None)

    @field_validator("project_name")
    @classmethod
    def no_spaces_at_ends(cls, v: str) -> str:
        return v.strip()

    @field_validator("agent_tools", mode="before")
    @classmethod
    def convert_agent_tools(cls, v: list[str]) -> list[AgentToolsEnum]:
        return [AgentToolsEnum(tool) for tool in v]

    @field_validator("ci_provider", mode="before")
    @classmethod
    def convert_ci_provider(cls, v: str | None) -> CIProviderEnum | None:
        return CIProviderEnum(v) if v else None

    @field_validator("database_provider", mode="before")
    @classmethod
    def convert_database_provider(cls, v: str | None) -> DatabaseProviderEnum | None:
        return DatabaseProviderEnum(v) if v else None

    @property
    def project_dir(self) -> Path:
        return self.base_dir / self.project_name

    @property
    def context(self) -> dict:
        return {
            "project_name": self.project_name,
            "project_title": self.project_title,
            "use_docker": self.use_docker,
            "use_database": self.use_database,
            "database_provider": self.database_provider,
            "dependencies": self._get_dependencies(),
        }

    @property
    def conditional_files(self) -> dict:
        return {
            ".dockerignore": self.use_docker,
            ".github/copilot-instructions.md": AgentToolsEnum.GITHUB_COPILOT in self.agent_tools,
            ".github/git-commit-instructions.md": AgentToolsEnum.GITHUB_COPILOT in self.agent_tools,
            "alembic.ini": self._use_alembic(),
            "src/core/common/db_connection.py": self.use_database,
        }

    @property
    def conditional_dirs(self) -> dict:
        return {
            "docker": self.use_docker,
            ".github": AgentToolsEnum.GITHUB_COPILOT in self.agent_tools
            or self.ci_provider == CIProviderEnum.GITHUB_ACTIONS,
            ".github/workflows": self.ci_provider == CIProviderEnum.GITHUB_ACTIONS,
            ".github/actions": self.ci_provider == CIProviderEnum.GITHUB_ACTIONS,
            "src/migrations": self._use_alembic(),
            "src/core/common": self.use_database,
        }

    def _use_alembic(self) -> bool:
        return self.database_provider in [DatabaseProviderEnum.POSTGRESQL]

    def _get_dependencies(self) -> list[str]:
        deps = [
            "fastapi>=0.128.0",
            "fastgear>=0.6.0",
            "loguru>=0.7.3",
            "pydantic>=2.12.5",
            "uvicorn>=0.40.0",
        ]

        if self.database_provider == DatabaseProviderEnum.POSTGRESQL:
            deps.append("asyncpg>=0.29.0")
            deps.append("alembic>=1.13.1")
            deps.append("greenlet>=3.3.2")

        return sorted(deps)
