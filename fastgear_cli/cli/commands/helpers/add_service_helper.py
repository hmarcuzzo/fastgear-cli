import questionary
import typer

from fastgear_cli.core.utils.python_validators_utils import (
    is_valid_python_identifier,
    is_valid_python_path,
)


def ask_repository_path() -> str | None:
    should_use_repository = questionary.confirm(
        "Do you want to inject a repository into this service?",
        default=False,
    ).ask()

    if not should_use_repository:
        return None

    response = questionary.text(
        "Repository import path (e.g. src.modules.user.repositories.user_repository.UserRepository):"
    ).ask()
    resolved_repository_path = response.strip() if response else ""
    return validate_repository_path(resolved_repository_path)


def validate_repository_path(value: str) -> str:
    resolved_repository_path = value.strip()
    if not resolved_repository_path:
        typer.secho(
            "Repository path is required when adding a service with repository.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    if "." not in resolved_repository_path:
        typer.secho(
            "Invalid repository path. Use a full import path ending with the class name.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    import_path, class_name = resolved_repository_path.rsplit(".", 1)
    if not is_valid_python_path(import_path) or not is_valid_python_identifier(class_name):
        typer.secho(
            "Invalid repository path. Use a full import path ending with the class name.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    return resolved_repository_path
