import re
from pathlib import Path
from typing import TYPE_CHECKING

import questionary
import typer

from fastgear_cli.core.render import run_ruff_format
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
        typer.secho(
            "Service path is required when adding a controller with service.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    if "." not in resolved_service_path:
        typer.secho(
            "Invalid service path. Use a full import path ending with the class name.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    import_path, class_name = resolved_service_path.rsplit(".", 1)
    if not is_valid_python_path(import_path) or not is_valid_python_identifier(class_name):
        typer.secho(
            "Invalid service path. Use a full import path ending with the class name.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

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
    init_path = base_dir / "controllers" / "__init__.py"
    router_name = f"{module_name}_router"
    import_line = f"from .{module_name}_controller import {router_name}"

    if not init_path.exists():
        content = f'{import_line}\n\n__all__ = ["{router_name}"]\n'
    else:
        current = init_path.read_text(encoding="utf-8")
        content = _merge_controller_init_content(current, import_line, router_name)
        if content == current:
            return None

    if dry_run:
        return init_path

    init_path.parent.mkdir(parents=True, exist_ok=True)
    init_path.write_text(content, encoding="utf-8")

    run_ruff_format(init_path, base_dir)

    return init_path


def _merge_controller_init_content(
    current: str,
    import_line: str,
    router_name: str,
) -> str:
    lines = current.splitlines()
    if import_line not in lines:
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

    merged = "\n".join(lines).rstrip("\n")
    all_match = re.search(r"__all__\s*=\s*\[(.*?)\]", merged, re.DOTALL)

    if all_match:
        raw_items = all_match.group(1)
        values = re.findall(r"""["']([^"']+)["']""", raw_items)
        if not values:
            values = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", raw_items)
        if router_name not in values:
            values.append(router_name)
        quoted_values = ", ".join(f'"{item}"' for item in values)
        all_value = f"__all__ = [{quoted_values}]"
        merged = f"{merged[: all_match.start()]}{all_value}{merged[all_match.end() :]}"
    else:
        if merged and not merged.endswith("\n\n"):
            merged = f"{merged}\n\n"
        merged = f'{merged}__all__ = ["{router_name}"]'

    return f"{merged.rstrip()}\n"
