import questionary


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
