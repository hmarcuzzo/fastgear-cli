from pathlib import Path

import typer

from fastgear_cli.cli.commands.helpers.add_entity_helper import handle_entity_files
from fastgear_cli.core.constants.enums import ElementTypeEnum
from fastgear_cli.core.filesystem import create_project
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
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what files would be created without actually creating them",
    ),
) -> None:
    config = AddElementConfig(
        base_dir=path, element_type=element_type, element_name=element_name, use_folders=use_folders
    )

    files = create_project(
        f"add/{config.element_type}/{config.structure}",
        config.base_dir,
        config.context,
        dry_run=dry_run,
    )

    match config.element_type:
        case ElementTypeEnum.ENTITY:
            files = handle_entity_files(config, dry_run=dry_run, files=files)

    if dry_run:
        FileTreeUtils.display_dry_run_output(files, config.base_dir)
        return

    typer.secho(
        f"Added {config.element_type} for module '{config.element_name}' successfully!",
        fg=typer.colors.GREEN,
    )
