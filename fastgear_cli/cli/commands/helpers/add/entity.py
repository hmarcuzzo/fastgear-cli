import re
from pathlib import Path

from fastgear_cli.core.models import AddElementConfig
from fastgear_cli.core.render import run_ruff_format
from fastgear_cli.core.utils.init_file_utils import update_module_init


def handle_entity_files(
    config: AddElementConfig,
    *,
    dry_run: bool,
    files: list[Path],
) -> list[Path]:
    if config.use_folders:
        entities_init_file = _update_entities_init(
            config.base_dir,
            config.element_name,
            config.context["element_class_name"],
            dry_run=dry_run,
        )
        if entities_init_file and entities_init_file not in files:
            files.append(entities_init_file)

    module_init_file = _update_parent_module_entities_init(
        base_dir=config.base_dir,
        entity_name=config.element_name,
        entity_class_name=config.context["element_class_name"],
        use_folders=config.use_folders,
        dry_run=dry_run,
    )
    if module_init_file and module_init_file not in files:
        files.append(module_init_file)

    return files


def _update_entities_init(
    base_dir: Path,
    module_name: str,
    module_class_name: str,
    *,
    dry_run: bool,
) -> Path | None:
    return update_module_init(
        base_dir=base_dir,
        module_dir="entities",
        module_name=module_name,
        symbol_name=module_class_name,
        source_suffix="entity",
        dry_run=dry_run,
    )


def _update_parent_module_entities_init(
    *,
    base_dir: Path,
    entity_name: str,
    entity_class_name: str,
    use_folders: bool,
    dry_run: bool,
) -> Path | None:
    init_path = base_dir / "__init__.py"
    if not init_path.exists():
        return None

    module_name = base_dir.name
    entities_list_name = f"{module_name}_entities"
    current_content = init_path.read_text(encoding="utf-8")
    if f"{entities_list_name} =" not in current_content:
        return None

    import_line = (
        f"from .entities import {entity_class_name}"
        if use_folders
        else f"from .{entity_name}_entity import {entity_class_name}"
    )

    content = _merge_required_line(current=current_content, required_line=import_line)
    content = _merge_symbol_list_assignment(
        current=content,
        list_name=entities_list_name,
        symbol_name=entity_class_name,
    )
    if content == current_content:
        return None

    if dry_run:
        return init_path

    init_path.write_text(content, encoding="utf-8")
    run_ruff_format(init_path, base_dir)
    return init_path


def _merge_symbol_list_assignment(
    *,
    current: str,
    list_name: str,
    symbol_name: str,
) -> str:
    assignment_pattern = re.compile(
        rf"{re.escape(list_name)}\s*=\s*\[(.*?)]",
        re.DOTALL,
    )
    assignment_match = assignment_pattern.search(current)

    if assignment_match:
        raw_values = assignment_match.group(1)
        symbols = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", raw_values)
        if symbol_name not in symbols:
            symbols.append(symbol_name)

        merged_assignment = f"{list_name} = [{', '.join(symbols)}]"
        merged = (
            f"{current[: assignment_match.start()]}"
            f"{merged_assignment}"
            f"{current[assignment_match.end() :]}"
        )
        return _lines_to_content(merged.splitlines())

    return _merge_required_line(
        current=current,
        required_line=f"{list_name} = [{symbol_name}]",
    )


def _merge_required_line(
    *,
    current: str,
    required_line: str,
) -> str:
    lines = current.splitlines()
    if required_line in lines:
        return current

    if required_line.startswith(("from ", "import ")):
        lines = _ensure_import_line(lines, required_line)
        return _lines_to_content(lines)

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
