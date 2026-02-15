from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from fastgear_cli.core.constants.enums import AgentToolsEnum, CIProviderEnum


class ProjectInitConfig(BaseModel):
    base_dir: Path = Field(default_factory=Path.cwd)
    project_name: str = Field(..., min_length=1)
    project_title: str = Field(..., min_length=1)
    use_docker: bool = Field(default=True)
    agent_tools: list[AgentToolsEnum | str] = Field(default_factory=list)
    ci_provider: CIProviderEnum | str | None = Field(default=None)

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

    @property
    def project_dir(self) -> Path:
        return self.base_dir / self.project_name

    @property
    def context(self) -> dict:
        return {
            "project_name": self.project_name,
            "project_title": self.project_title,
            "use_docker": self.use_docker,
        }

    @property
    def conditional_files(self) -> dict:
        return {
            ".dockerignore": self.use_docker,
            "copilot-instructions.md": AgentToolsEnum.GITHUB_COPILOT in self.agent_tools,
            "git-commit-instructions.md": AgentToolsEnum.GITHUB_COPILOT in self.agent_tools,
        }

    @property
    def conditional_dirs(self) -> dict:
        return {
            "docker": self.use_docker,
            ".github": AgentToolsEnum.GITHUB_COPILOT in self.agent_tools
            or self.ci_provider == CIProviderEnum.GITHUB_ACTIONS,
            ".github/workflows": self.ci_provider == CIProviderEnum.GITHUB_ACTIONS,
            ".github/actions": self.ci_provider == CIProviderEnum.GITHUB_ACTIONS,
        }
