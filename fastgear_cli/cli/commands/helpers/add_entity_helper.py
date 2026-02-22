import re
from pathlib import Path

from fastgear_cli.core.models import AddElementConfig
from fastgear_cli.core.render import run_ruff_format


def handle_entity_files(
    config: AddElementConfig,
    *,
    dry_run: bool,
    files: list[Path],
) -> list[Path]:
    if config.use_folders:
        init_file = _update_entities_init(
            config.base_dir,
            config.element_name,
            config.context["element_class_name"],
            dry_run=dry_run,
        )
        if init_file and init_file not in files:
            files.append(init_file)

    return files


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

    run_ruff_format(init_path, base_dir)

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
