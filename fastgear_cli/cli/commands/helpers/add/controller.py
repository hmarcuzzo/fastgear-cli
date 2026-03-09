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


def ask_service_path() -> str | None:
    should_use_service = questionary.confirm(
        "Do you want to inject a service into this controller?",
        default=False,
    ).ask()

    if not should_use_service:
        return None

    response = questionary.text(
        "Service import path (e.g. src.modules.user.services.user_service.UserService):"
    ).ask()
    resolved_service_path = response.strip() if response else ""
    return validate_service_path(resolved_service_path)


def validate_service_path(value: str) -> str:
    resolved_service_path = value.strip()
    if not resolved_service_path:
        raise InvalidInputError("Service path is required when adding a controller with service.")

    if "." not in resolved_service_path:
        raise InvalidInputError(
            "Invalid service path. Use a full import path ending with the class name."
        )

    import_path, class_name = resolved_service_path.rsplit(".", 1)
    if not is_valid_python_path(import_path) or not is_valid_python_identifier(class_name):
        raise InvalidInputError(
            "Invalid service path. Use a full import path ending with the class name."
        )

    return resolved_service_path


def handle_controller_files(
    config: "AddElementConfig",
    *,
    dry_run: bool,
    files: list[Path],
) -> list[Path]:
    if config.use_folders:
        init_file = _update_controllers_init(
            config.base_dir,
            config.element_name,
            dry_run=dry_run,
        )
        if init_file and init_file not in files:
            files.append(init_file)

    return files


def _update_controllers_init(
    base_dir: Path,
    module_name: str,
    *,
    dry_run: bool,
) -> Path | None:
    return update_module_init(
        base_dir=base_dir,
        module_dir="controllers",
        module_name=module_name,
        symbol_name=f"{module_name}_router",
        source_suffix="controller",
        dry_run=dry_run,
    )
