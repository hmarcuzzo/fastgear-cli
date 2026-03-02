import re

import questionary
import typer


def ask_entity_path() -> str:
    response = questionary.text("Entity import path (e.g. src.modules.user.entities.User):").ask()

    resolved_entity_path = response.strip() if response else ""
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
    if not _is_valid_python_path(import_path) or not _is_valid_python_identifier(class_name):
        typer.secho(
            "Invalid entity path. Use a full import path ending with the class name.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    return resolved_entity_path


def _is_valid_python_path(path: str) -> bool:
    return all(_is_valid_python_identifier(part) for part in path.split("."))


def _is_valid_python_identifier(value: str) -> bool:
    return re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", value) is not None
