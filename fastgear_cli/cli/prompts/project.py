import questionary

from fastgear_cli.core.constants.enums.agent_tools_enum import AgentToolsEnum


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
