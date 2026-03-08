from pathlib import Path

from fastgear_cli.core.models import AddElementConfig
from fastgear_cli.core.utils.init_file_utils import update_module_init


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
    return update_module_init(
        base_dir=base_dir,
        module_dir="entities",
        module_name=module_name,
        symbol_name=module_class_name,
        source_suffix="entity",
        dry_run=dry_run,
    )
