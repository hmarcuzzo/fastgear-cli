from pathlib import Path

from fastgear_cli.core.models import AddElementConfig
from fastgear_cli.core.render import run_ruff_format
from fastgear_cli.core.utils.init_content_merge_utils import (
    merge_required_line,
    merge_symbol_list_assignment,
)
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

    content = merge_required_line(current=current_content, required_line=import_line)
    content = merge_symbol_list_assignment(
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
