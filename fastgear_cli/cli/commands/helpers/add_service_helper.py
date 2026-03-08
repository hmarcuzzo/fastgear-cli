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
        raise InvalidInputError(
            "Repository path is required when adding a service with repository."
        )

    if "." not in resolved_repository_path:
        raise InvalidInputError(
            "Invalid repository path. Use a full import path ending with the class name."
        )

    import_path, class_name = resolved_repository_path.rsplit(".", 1)
    if not is_valid_python_path(import_path) or not is_valid_python_identifier(class_name):
        raise InvalidInputError(
            "Invalid repository path. Use a full import path ending with the class name."
        )

    return resolved_repository_path


def handle_service_files(
    config: "AddElementConfig",
    *,
    dry_run: bool,
    files: list[Path],
) -> list[Path]:
    if config.use_folders:
        init_file = _update_services_init(
            config.base_dir,
            config.element_name,
            config.context["element_class_name"],
            dry_run=dry_run,
        )
        if init_file and init_file not in files:
            files.append(init_file)

    return files


def _update_services_init(
    base_dir: Path,
    module_name: str,
    module_class_name: str,
    *,
    dry_run: bool,
) -> Path | None:
    return update_module_init(
        base_dir=base_dir,
        module_dir="services",
        module_name=module_name,
        symbol_name=f"{module_class_name}Service",
        source_suffix="service",
        dry_run=dry_run,
    )
