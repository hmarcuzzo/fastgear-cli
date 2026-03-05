import questionary
import typer

from fastgear_cli.core.utils.python_validators_utils import (
    is_valid_python_identifier,
    is_valid_python_path,
)


def ask_entity_path() -> str:
    response = questionary.text("Entity import path (e.g. src.modules.user.entities.User):").ask()
    resolved_entity_path = response.strip() if response else ""
    return validate_entity_path(resolved_entity_path)


def validate_entity_path(value: str) -> str:
    resolved_entity_path = value.strip()
    if not resolved_entity_path:
        typer.secho(
            "Entity path is required when adding a repository.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    if "." not in resolved_entity_path:
        typer.secho(
            "Invalid entity path. Use a full import path ending with the class name.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    import_path, class_name = resolved_entity_path.rsplit(".", 1)
    if not is_valid_python_path(import_path) or not is_valid_python_identifier(class_name):
        typer.secho(
            "Invalid entity path. Use a full import path ending with the class name.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    return resolved_entity_path
