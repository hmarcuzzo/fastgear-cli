import re
import subprocess
from pathlib import Path

import typer

from fastgear_cli.core.filesystem import create_project
from fastgear_cli.core.utils.file_tree_utils import FileTreeUtils

add_app = typer.Typer(help="Add new components to an existing FastGear project")

SUPPORTED_COMPONENTS = ["module", "controller", "service", "entity", "repository"]
IMPLEMENTED_COMPONENTS = {"entity", "repository"}


@add_app.command()
def add(
    element_type: str = typer.Argument(
        ...,
        help="Element type: module/controller/service/entity/repository",
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
    element_t_normalized = element_type.strip().lower()

    if element_t_normalized not in SUPPORTED_COMPONENTS:
        typer.secho(
            "Invalid component type. Use one of: module/controller/service/entity/repository",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    if element_t_normalized not in IMPLEMENTED_COMPONENTS:
        typer.secho(
            f"Component '{element_t_normalized}' is not implemented yet.",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(code=1)

    base_dir = path if path else Path.cwd()
    element_name_normalized = _normalize_name(element_name)
    structure = "folder" if use_folders else "flat"

    context = {
        "element_name": element_name_normalized,
        "element_class_name": _to_pascal_case(element_name_normalized),
    }

    files = create_project(
        f"add/new_{element_t_normalized}/{structure}",
        base_dir,
        context,
        dry_run=dry_run,
    )

    if element_t_normalized == "entity" and use_folders:
        init_file = _update_entities_init(
            base_dir,
            element_name_normalized,
            context["module_class_name"],
            dry_run=dry_run,
        )
        if init_file and init_file not in files:
            files.append(init_file)

    if dry_run:
        FileTreeUtils.display_dry_run_output(files, base_dir)
        return

    if not files:
        typer.secho(
            f"No new files created. The {element_t_normalized} may already exist.",
            fg=typer.colors.YELLOW,
        )
        return

    typer.secho(
        f"Added {element_t_normalized} for module '{element_name_normalized}' successfully!",
        fg=typer.colors.GREEN,
    )


def _normalize_name(name: str) -> str:
    value = name.strip()
    if not value:
        typer.secho("Component name cannot be empty.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    value = value.replace("-", "_").replace(" ", "_")
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"[^a-zA-Z0-9_]", "", value)
    value = re.sub(r"_+", "_", value).strip("_").lower()

    if not value:
        typer.secho(
            "Component name must contain letters or numbers.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    return value


def _to_pascal_case(value: str) -> str:
    return "".join(part.capitalize() for part in value.split("_") if part)


def _update_entities_init(
    base_dir: Path,
    module_name: str,
    module_class_name: str,
    *,
    dry_run: bool,
) -> Path | None:
    init_path = base_dir / "entities" / "__init__.py"
    class_name = f"{module_class_name}"
    import_line = f"from .{module_name}_entity import {class_name}"

    if not init_path.exists():
        content = f'{import_line}\n\n__all__ = ["{class_name}"]\n'
    else:
        current = init_path.read_text(encoding="utf-8")
        content = _merge_entity_init_content(current, import_line, class_name)
        if content == current:
            return None

    if dry_run:
        return init_path

    init_path.parent.mkdir(parents=True, exist_ok=True)
    init_path.write_text(content, encoding="utf-8")

    subprocess.run(
        ["uv", "run", "ruff", "format", str(init_path)],
        check=False,
        capture_output=True,
    )

    return init_path


def _merge_entity_init_content(
    current: str,
    import_line: str,
    class_name: str,
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
        if class_name not in values:
            values.append(class_name)
        quoted_values = ", ".join(f'"{item}"' for item in values)
        all_value = f"__all__ = [{quoted_values}]"
        merged = f"{merged[: all_match.start()]}{all_value}{merged[all_match.end() :]}"
    else:
        if merged and not merged.endswith("\n\n"):
            merged = f"{merged}\n\n"
        merged = f'{merged}__all__ = ["{class_name}"]'

    return f"{merged.rstrip()}\n"
