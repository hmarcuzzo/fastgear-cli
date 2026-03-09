from pathlib import Path
from typing import TYPE_CHECKING

import questionary

from fastgear_cli.core.exceptions import InvalidInputError
from fastgear_cli.core.render import run_ruff_format
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
        controllers_init_file = _update_controllers_init(
            config.base_dir,
            config.element_name,
            dry_run=dry_run,
        )
        if controllers_init_file and controllers_init_file not in files:
            files.append(controllers_init_file)

    module_init_file = _update_parent_module_router_init(
        base_dir=config.base_dir,
        controller_name=config.element_name,
        use_folders=config.use_folders,
        dry_run=dry_run,
    )
    if module_init_file and module_init_file not in files:
        files.append(module_init_file)

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


def _update_parent_module_router_init(
    *,
    base_dir: Path,
    controller_name: str,
    use_folders: bool,
    dry_run: bool,
) -> Path | None:
    init_path = base_dir / "__init__.py"
    if not init_path.exists():
        return None

    module_name = base_dir.name
    router_anchor_line = f"{module_name}_module_router = APIRouter()"
    current_content = init_path.read_text(encoding="utf-8")
    if router_anchor_line not in current_content:
        return None

    import_line = (
        f"from .controllers import {controller_name}_router"
        if use_folders
        else f"from .{controller_name}_controller import {controller_name}_router"
    )
    include_line = f"{module_name}_module_router.include_router({controller_name}_router)"

    content = _merge_required_line(current=current_content, required_line=import_line)
    content = _merge_required_line(
        current=content,
        required_line=include_line,
        anchor_line=router_anchor_line,
    )
    if content == current_content:
        return None

    if dry_run:
        return init_path

    init_path.write_text(content, encoding="utf-8")
    run_ruff_format(init_path, base_dir)
    return init_path


def _merge_required_line(
    *,
    current: str,
    required_line: str,
    anchor_line: str | None = None,
) -> str:
    lines = current.splitlines()
    if required_line in lines:
        return current

    if required_line.startswith(("from ", "import ")):
        lines = _ensure_import_line(lines, required_line)
        return _lines_to_content(lines)

    if anchor_line and anchor_line in lines:
        anchor_index = lines.index(anchor_line)
        lines.insert(anchor_index + 1, required_line)
    else:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append(required_line)

    return _lines_to_content(lines)


def _ensure_import_line(lines: list[str], import_line: str) -> list[str]:
    if import_line in lines:
        return lines

    insert_idx = 0
    while insert_idx < len(lines) and (
        lines[insert_idx].startswith("from ")
        or lines[insert_idx].startswith("import ")
        or not lines[insert_idx].strip()
    ):
        insert_idx += 1

    lines.insert(insert_idx, import_line)
    if insert_idx > 0 and lines[insert_idx - 1].strip():
        lines.insert(insert_idx, "")

    return lines


def _lines_to_content(lines: list[str]) -> str:
    if not lines:
        return ""
    return f"{'\n'.join(lines).rstrip()}\n"
