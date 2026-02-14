import questionary

from fastgear_cli.core.constants.enums import AgentToolsEnum, CIProviderEnum


def ask_project_name() -> str:
    return questionary.text(
        "Project name:",
        validate=lambda x: True if x.strip() else "Name cannot be empty",
    ).ask()


def confirm_project_title(project_name: str) -> str:
    project_title = project_name.translate(str.maketrans("-_", "  ")).title()
    return questionary.text(
        "Project title:",
        default=project_title,
    ).ask()


def ask_agent_tools() -> list[str]:
    use_agent = questionary.confirm(
        "Use AI agent tools?",
        default=False,
    ).ask()

    if not use_agent:
        return []

    agent_choices = questionary.checkbox(
        "Select agent tools:",
        choices=[AgentToolsEnum.GITHUB_COPILOT],
    ).ask()

    return agent_choices or []


def ask_ci_provider() -> str | None:
    use_ci = questionary.confirm(
        "Use CI/CD pipeline?",
        default=True,
    ).ask()

    if not use_ci:
        return None

    return questionary.select(
        "Select CI/CD provider:",
        choices=[CIProviderEnum.GITHUB_ACTIONS],
    ).ask()
