from pathlib import Path

import typer

from fastgear_cli.cli.commands.helpers.add_controller_helper import handle_controller_files
from fastgear_cli.cli.commands.helpers.add_entity_helper import handle_entity_files
from fastgear_cli.core.constants.enums import ElementTypeEnum
from fastgear_cli.core.filesystem import create_template
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
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what files would be created without actually creating them",
    ),
) -> None:
    config = AddElementConfig(
        base_dir=path,
        element_type=element_type,
        element_name=element_name,
        use_folders=use_folders,
        entity_path=entity_path,
        repository_path=repository_path,
        service_path=service_path,
    )

    files = create_template(
        f"add/{config.element_type}/{config.structure}",
        config.base_dir,
        config.context,
        dry_run=dry_run,
    )

    match config.element_type:
        case ElementTypeEnum.CONTROLLER:
            files = handle_controller_files(config, dry_run=dry_run, files=files)
        case ElementTypeEnum.ENTITY:
            files = handle_entity_files(config, dry_run=dry_run, files=files)

    if dry_run:
        FileTreeUtils.display_dry_run_output(files, config.base_dir)
        return

    typer.secho(
        f"\nAdded {config.element_type} successfully!",
        fg=typer.colors.GREEN,
    )
