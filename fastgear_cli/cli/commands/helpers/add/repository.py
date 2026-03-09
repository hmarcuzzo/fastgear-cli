from pathlib import Path
from typing import TYPE_CHECKING

import questionary

from fastgear_cli.core.exceptions import InvalidInputError
from fastgear_cli.core.utils.init_file_utils import update_module_init
from fastgear_cli.core.utils.python_validators_utils import (
    is_valid_python_identifier,
    is_valid_python_path,
)

if TYPE_CHECKING:
    from fastgear_cli.core.models import AddElementConfig


def ask_entity_path() -> str | None:
    should_use_entity = questionary.confirm(
        "Do you want to inject an entity into this repository?",
        default=False,
    ).ask()

    if not should_use_entity:
        return None

    response = questionary.text("Entity import path (e.g. src.modules.user.entities.User):").ask()
    resolved_entity_path = response.strip() if response else ""
    return validate_entity_path(resolved_entity_path)


def validate_entity_path(value: str) -> str:
    resolved_entity_path = value.strip()
    if not resolved_entity_path:
        raise InvalidInputError("Entity path is required when adding a repository.")

    if "." not in resolved_entity_path:
        raise InvalidInputError(
            "Invalid entity path. Use a full import path ending with the class name."
        )

    import_path, class_name = resolved_entity_path.rsplit(".", 1)
    if not is_valid_python_path(import_path) or not is_valid_python_identifier(class_name):
        raise InvalidInputError(
            "Invalid entity path. Use a full import path ending with the class name."
        )

    return resolved_entity_path


def handle_repository_files(
    config: "AddElementConfig",
    *,
    dry_run: bool,
    files: list[Path],
) -> list[Path]:
    if config.use_folders:
        init_file = _update_repositories_init(
            config.base_dir,
            config.element_name,
            config.context["element_class_name"],
            dry_run=dry_run,
        )
        if init_file and init_file not in files:
            files.append(init_file)

    return files


def _update_repositories_init(
    base_dir: Path,
    module_name: str,
    module_class_name: str,
    *,
    dry_run: bool,
) -> Path | None:
    return update_module_init(
        base_dir=base_dir,
        module_dir="repositories",
        module_name=module_name,
        symbol_name=f"{module_class_name}Repository",
        source_suffix="repository",
        dry_run=dry_run,
    )
