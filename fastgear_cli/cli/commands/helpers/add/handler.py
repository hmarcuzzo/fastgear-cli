from collections.abc import Callable
from pathlib import Path

from fastgear_cli.cli.commands.helpers.add.controller import handle_controller_files
from fastgear_cli.cli.commands.helpers.add.entity import handle_entity_files
from fastgear_cli.cli.commands.helpers.add.repository import handle_repository_files
from fastgear_cli.cli.commands.helpers.add.service import handle_service_files
from fastgear_cli.core.constants.enums import ElementTypeEnum
from fastgear_cli.core.filesystem import create_template
from fastgear_cli.core.models import AddElementConfig

AddFileHandler = Callable[..., list[Path]]
ADD_FILE_HANDLERS: dict[ElementTypeEnum, AddFileHandler] = {
    ElementTypeEnum.CONTROLLER: handle_controller_files,
    ElementTypeEnum.ENTITY: handle_entity_files,
    ElementTypeEnum.REPOSITORY: handle_repository_files,
    ElementTypeEnum.SERVICE: handle_service_files,
}


def create_component_files(config: AddElementConfig, *, dry_run: bool) -> list[Path]:
    files = create_template(
        f"add/{config.element_type}/{config.structure}",
        config.base_dir,
        config.context,
        dry_run=dry_run,
    )

    handler = ADD_FILE_HANDLERS.get(config.element_type)
    if handler:
        files = handler(config, dry_run=dry_run, files=files)

    return files
