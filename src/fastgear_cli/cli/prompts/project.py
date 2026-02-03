import questionary


def ask_project_name() -> str:
    return questionary.text(
        "Project name:",
        validate=lambda x: True if x.strip() else "Name cannot be empty",
    ).ask()
