from collections.abc import Callable
from pathlib import Path

import typer

from fastgear_cli.cli.commands.helpers.add_controller_helper import (
    ask_service_path,
    handle_controller_files,
    validate_service_path,
)
from fastgear_cli.cli.commands.helpers.add_entity_helper import handle_entity_files
from fastgear_cli.cli.commands.helpers.add_repository_helper import (
    ask_entity_path,
    validate_entity_path,
)
from fastgear_cli.cli.commands.helpers.add_service_helper import (
    ask_repository_path,
    validate_repository_path,
)
from fastgear_cli.core.constants.enums import ElementTypeEnum
from fastgear_cli.core.exceptions import FastgearCliError
from fastgear_cli.core.filesystem import create_template
from fastgear_cli.core.models import AddElementConfig
from fastgear_cli.core.models.add_element_config import (
    normalize_element_name,
    parse_element_type,
)
from fastgear_cli.core.utils.file_tree_utils import FileTreeUtils

add_app = typer.Typer(help="Add new components to an existing FastGear project")

type AddFileHandler = Callable[..., list[Path]]
ADD_FILE_HANDLERS: dict[ElementTypeEnum, AddFileHandler] = {
    ElementTypeEnum.CONTROLLER: handle_controller_files,
    ElementTypeEnum.ENTITY: handle_entity_files,
}


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
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what files would be created without actually creating them",
    ),
) -> None:
    try:
        resolved_element_type = parse_element_type(element_type)
        resolved_element_name = normalize_element_name(element_name)
        resolved_entity_path, resolved_repository_path, resolved_service_path = _resolve_paths(
            element_type=resolved_element_type,
            entity_path=entity_path,
            repository_path=repository_path,
            service_path=service_path,
        )

        config = AddElementConfig(
            base_dir=path,
            element_type=resolved_element_type,
            element_name=resolved_element_name,
            use_folders=use_folders,
            entity_path=resolved_entity_path,
            repository_path=resolved_repository_path,
            service_path=resolved_service_path,
        )

        files = create_template(
            f"add/{config.element_type}/{config.structure}",
            config.base_dir,
            config.context,
            dry_run=dry_run,
        )

        handler = ADD_FILE_HANDLERS.get(config.element_type)
        if handler:
            files = handler(config, dry_run=dry_run, files=files)

        if dry_run:
            FileTreeUtils.display_dry_run_output(files, config.base_dir)
            return

        typer.secho(
            f"\nAdded {config.element_type} successfully!",
            fg=typer.colors.GREEN,
        )
    except FastgearCliError as error:
        typer.secho(str(error), fg=typer.colors.RED)
        raise typer.Exit(code=1) from error


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

    if element_type == ElementTypeEnum.REPOSITORY:
        if resolved_entity_path is None:
            resolved_entity_path = ask_entity_path()
        else:
            resolved_entity_path = validate_entity_path(resolved_entity_path)

    if element_type == ElementTypeEnum.SERVICE:
        if resolved_repository_path is None:
            resolved_repository_path = ask_repository_path()
        else:
            resolved_repository_path = validate_repository_path(resolved_repository_path)

    if element_type == ElementTypeEnum.CONTROLLER:
        if resolved_service_path is None:
            resolved_service_path = ask_service_path()
        else:
            resolved_service_path = validate_service_path(resolved_service_path)

    return resolved_entity_path, resolved_repository_path, resolved_service_path
