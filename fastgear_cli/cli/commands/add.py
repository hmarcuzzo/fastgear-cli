import re
from pathlib import Path

import typer

from fastgear_cli.cli.commands.helpers.add.controller import ask_service_path, validate_service_path
from fastgear_cli.cli.commands.helpers.add.handler import create_component_files
from fastgear_cli.cli.commands.helpers.add.module import add_module
from fastgear_cli.cli.commands.helpers.add.repository import ask_entity_path, validate_entity_path
from fastgear_cli.cli.commands.helpers.add.service import (
    ask_repository_path,
    validate_repository_path,
)
from fastgear_cli.core.constants.enums import ElementTypeEnum
from fastgear_cli.core.exceptions import FastgearCliError, InvalidInputError
from fastgear_cli.core.models import AddElementConfig
from fastgear_cli.core.utils.file_tree_utils import FileTreeUtils

add_app = typer.Typer(help="Add new components to an existing FastGear project")


@add_app.command()
def add(
    element_type: str = typer.Argument(
        ...,
        help="Element type: module | controller | service | entity | repository",
    ),
    element_name: str = typer.Argument(..., help="Module name"),
    path: Path = typer.Option(
        None,
        "--path",
        "-p",
        file_okay=False,
        dir_okay=True,
        help="Base path where files should be created (defaults to current directory)",
    ),
    use_folders: bool = typer.Option(
        True,
        "--use-folders/--no-use-folders",
        help="Use nested folders (e.g. <module>/entities). Default is enabled.",
    ),
    entity_path: str | None = typer.Option(
        None,
        "--entity-path",
        help="Entity import path used by repository (e.g. src.modules.user.entities.User)",
    ),
    repository_path: str | None = typer.Option(
        None,
        "--repository-path",
        help="Repository import path used by service (optional, e.g. src.modules.user.repositories.user_repository.UserRepository)",
    ),
    service_path: str | None = typer.Option(
        None,
        "--service-path",
        help="Service import path used by controller (optional, e.g. src.modules.user.services.user_service.UserService)",
    ),
    module_components: str | None = typer.Option(
        None,
        "--module-components",
        help="Comma-separated components for module: controller,service,repository,entity (if omitted, asks interactively)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what files would be created without actually creating them",
    ),
) -> None:
    try:
        resolved_element_type = _parse_element_type(element_type)
        resolved_element_name = _normalize_element_name(element_name)
        base_dir = path or Path.cwd()

        if resolved_element_type == ElementTypeEnum.MODULE:
            files = add_module(
                base_dir=base_dir,
                module_name=resolved_element_name,
                use_folders=use_folders,
                entity_path=entity_path,
                repository_path=repository_path,
                service_path=service_path,
                module_components=module_components,
                dry_run=dry_run,
            )
            output_base_dir = base_dir
            success_message = f"\nAdded module {resolved_element_name} successfully!"
        else:
            if module_components is not None:
                raise InvalidInputError(
                    "--module-components can only be used with element type module."
                )

            resolved_entity_path, resolved_repository_path, resolved_service_path = _resolve_paths(
                element_type=resolved_element_type,
                entity_path=entity_path,
                repository_path=repository_path,
                service_path=service_path,
            )
            config = AddElementConfig(
                base_dir=base_dir,
                element_type=resolved_element_type,
                element_name=resolved_element_name,
                use_folders=use_folders,
                entity_path=resolved_entity_path,
                repository_path=resolved_repository_path,
                service_path=resolved_service_path,
            )
            files = create_component_files(config, dry_run=dry_run)
            output_base_dir = config.base_dir
            success_message = f"\nAdded {config.element_type} successfully!"

        if dry_run:
            FileTreeUtils.display_dry_run_output(files, output_base_dir)
            return

        typer.secho(success_message, fg=typer.colors.GREEN)
    except FastgearCliError as error:
        typer.secho(str(error), fg=typer.colors.RED)
        raise typer.Exit(code=1) from error


def _parse_element_type(value: str) -> ElementTypeEnum:
    try:
        return ElementTypeEnum(value.strip().lower())
    except ValueError as error:
        raise InvalidInputError(
            "Invalid element type. Use one of: module | controller | service | entity | repository"
        ) from error


def _normalize_element_name(value: str) -> str:
    normalized = value.strip()
    normalized = normalized.replace("-", "_").replace(" ", "_")
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized)
    normalized = re.sub(r"[^a-zA-Z0-9_]", "", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_").lower()

    if not normalized:
        raise InvalidInputError("Element name must contain letters or numbers.")

    return normalized


def _resolve_paths(
    *,
    element_type: ElementTypeEnum,
    entity_path: str | None,
    repository_path: str | None,
    service_path: str | None,
) -> tuple[str | None, str | None, str | None]:
    resolved_entity_path = entity_path
    resolved_repository_path = repository_path
    resolved_service_path = service_path

    if element_type == ElementTypeEnum.REPOSITORY and resolved_entity_path is None:
        resolved_entity_path = ask_entity_path()
    elif element_type == ElementTypeEnum.REPOSITORY:
        resolved_entity_path = validate_entity_path(resolved_entity_path)

    if element_type == ElementTypeEnum.SERVICE and resolved_repository_path is None:
        resolved_repository_path = ask_repository_path()
    elif element_type == ElementTypeEnum.SERVICE:
        resolved_repository_path = validate_repository_path(resolved_repository_path)

    if element_type == ElementTypeEnum.CONTROLLER and resolved_service_path is None:
        resolved_service_path = ask_service_path()
    elif element_type == ElementTypeEnum.CONTROLLER:
        resolved_service_path = validate_service_path(resolved_service_path)

    return resolved_entity_path, resolved_repository_path, resolved_service_path
