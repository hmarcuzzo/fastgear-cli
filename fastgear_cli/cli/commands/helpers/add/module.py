import re
from pathlib import Path

import questionary
from jinja2 import Environment, FileSystemLoader, select_autoescape

from fastgear_cli.cli.commands.helpers.add.controller import validate_service_path
from fastgear_cli.cli.commands.helpers.add.handler import create_component_files
from fastgear_cli.cli.commands.helpers.add.repository import validate_entity_path
from fastgear_cli.cli.commands.helpers.add.service import validate_repository_path
from fastgear_cli.configs.settings import ROOT_DIR
from fastgear_cli.core.constants.enums import ElementTypeEnum
from fastgear_cli.core.exceptions import InvalidInputError, TemplateConflictError
from fastgear_cli.core.models import AddElementConfig
from fastgear_cli.core.render import run_ruff_format

MODULE_PROMPT_CHOICES = (
    ElementTypeEnum.CONTROLLER,
    ElementTypeEnum.SERVICE,
    ElementTypeEnum.REPOSITORY,
    ElementTypeEnum.ENTITY,
)
MODULE_GENERATION_ORDER = (
    ElementTypeEnum.ENTITY,
    ElementTypeEnum.REPOSITORY,
    ElementTypeEnum.SERVICE,
    ElementTypeEnum.CONTROLLER,
)


def add_module(
    *,
    base_dir: Path,
    module_name: str,
    use_folders: bool,
    entity_path: str | None,
    repository_path: str | None,
    service_path: str | None,
    module_components: str | None,
    dry_run: bool,
) -> list[Path]:
    module_dir = base_dir / module_name
    components = _resolve_module_components(module_components)
    module_import_root = _resolve_module_import_root(base_dir=base_dir, module_name=module_name)
    created_files: list[Path] = []

    for component in components:
        resolved_entity_path, resolved_repository_path, resolved_service_path = (
            _resolve_module_paths(
                component=component,
                module_name=module_name,
                selected_components=set(components),
                module_import_root=module_import_root,
                use_folders=use_folders,
                entity_path=entity_path,
                repository_path=repository_path,
                service_path=service_path,
            )
        )

        config = AddElementConfig(
            base_dir=module_dir,
            element_type=component,
            element_name=module_name,
            use_folders=use_folders,
            entity_path=resolved_entity_path,
            repository_path=resolved_repository_path,
            service_path=resolved_service_path,
        )

        try:
            component_files = create_component_files(config, dry_run=dry_run)
        except TemplateConflictError:
            continue
        _append_unique_files(created_files, component_files)

    module_init = _update_module_init_from_template(
        module_dir=module_dir,
        module_name=module_name,
        use_folders=use_folders,
        has_controller=ElementTypeEnum.CONTROLLER in components,
        has_entity=ElementTypeEnum.ENTITY in components,
        dry_run=dry_run,
    )
    if module_init and module_init not in created_files:
        created_files.append(module_init)

    if not created_files:
        raise TemplateConflictError("No new files created. The content may already exist.")

    return created_files


def _resolve_module_components(module_components: str | None) -> list[ElementTypeEnum]:
    if module_components is None:
        selected = questionary.checkbox(
            "Which components do you want to add to this module?",
            choices=[choice.value for choice in MODULE_PROMPT_CHOICES],
        ).ask()
        values = selected or []
    else:
        values = [item.strip().lower() for item in module_components.split(",") if item.strip()]

    return _parse_module_components(values)


def _parse_module_components(values: list[str]) -> list[ElementTypeEnum]:
    if not values:
        raise InvalidInputError(
            "At least one component is required for module. Use: controller, service, repository, entity."
        )

    selected: set[ElementTypeEnum] = set()
    valid_components = {choice.value for choice in MODULE_PROMPT_CHOICES}

    for value in values:
        if value not in valid_components:
            raise InvalidInputError(
                "Invalid module component. Use only: controller, service, repository, entity."
            )
        selected.add(ElementTypeEnum(value))

    return [component for component in MODULE_GENERATION_ORDER if component in selected]


def _resolve_module_paths(
    *,
    component: ElementTypeEnum,
    module_name: str,
    selected_components: set[ElementTypeEnum],
    module_import_root: str,
    use_folders: bool,
    entity_path: str | None,
    repository_path: str | None,
    service_path: str | None,
) -> tuple[str | None, str | None, str | None]:
    module_class_name = "".join(part.capitalize() for part in module_name.split("_") if part)
    resolved_entity_path = entity_path
    resolved_repository_path = repository_path
    resolved_service_path = service_path

    if component == ElementTypeEnum.REPOSITORY:
        if resolved_entity_path is not None:
            resolved_entity_path = validate_entity_path(resolved_entity_path)
        elif ElementTypeEnum.ENTITY in selected_components:
            resolved_entity_path = _build_module_entity_path(
                module_class_name=module_class_name,
                module_import_root=module_import_root,
                use_folders=use_folders,
            )

    if component == ElementTypeEnum.SERVICE:
        if resolved_repository_path is not None:
            resolved_repository_path = validate_repository_path(resolved_repository_path)
        elif ElementTypeEnum.REPOSITORY in selected_components:
            resolved_repository_path = _build_module_repository_path(
                module_class_name=module_class_name,
                module_import_root=module_import_root,
                use_folders=use_folders,
            )

    if component == ElementTypeEnum.CONTROLLER:
        if resolved_service_path is not None:
            resolved_service_path = validate_service_path(resolved_service_path)
        elif ElementTypeEnum.SERVICE in selected_components:
            resolved_service_path = _build_module_service_path(
                module_class_name=module_class_name,
                module_import_root=module_import_root,
                use_folders=use_folders,
            )

    return resolved_entity_path, resolved_repository_path, resolved_service_path


def _resolve_module_import_root(*, base_dir: Path, module_name: str) -> str:
    module_dir = (base_dir / module_name).resolve()
    cwd = Path.cwd().resolve()
    try:
        relative_module_dir = module_dir.relative_to(cwd)
    except ValueError as error:
        raise InvalidInputError(
            "Module path must be inside the current project root to build absolute imports."
        ) from error

    if not relative_module_dir.parts:
        raise InvalidInputError("Unable to resolve module import root from the provided path.")

    return ".".join(relative_module_dir.parts)


def _build_module_entity_path(
    *,
    module_class_name: str,
    module_import_root: str,
    use_folders: bool,
) -> str:
    if use_folders:
        return f"{module_import_root}.entities.{module_class_name}"
    return f"{module_import_root}.{module_class_name}"


def _build_module_repository_path(
    *,
    module_class_name: str,
    module_import_root: str,
    use_folders: bool,
) -> str:
    repository_class_name = f"{module_class_name}Repository"
    if use_folders:
        return f"{module_import_root}.repositories.{repository_class_name}"
    return f"{module_import_root}.{repository_class_name}"


def _build_module_service_path(
    *,
    module_class_name: str,
    module_import_root: str,
    use_folders: bool,
) -> str:
    service_class_name = f"{module_class_name}Service"
    if use_folders:
        return f"{module_import_root}.services.{service_class_name}"
    return f"{module_import_root}.{service_class_name}"


def _append_unique_files(base_files: list[Path], new_files: list[Path]) -> None:
    for file_path in new_files:
        if file_path not in base_files:
            base_files.append(file_path)


def _update_module_init_from_template(
    *,
    module_dir: Path,
    module_name: str,
    use_folders: bool,
    has_controller: bool,
    has_entity: bool,
    dry_run: bool,
) -> Path | None:
    init_path = module_dir / "__init__.py"
    context = _build_module_template_context(
        module_name=module_name,
        has_controller=has_controller,
        has_entity=has_entity,
    )
    template_content = _render_module_init_template(
        use_folders=use_folders,
        context=context,
    )
    if not has_controller and not has_entity:
        template_content = ""

    if not init_path.exists():
        content = template_content
        if dry_run:
            return init_path

        init_path.parent.mkdir(parents=True, exist_ok=True)
        init_path.write_text(content, encoding="utf-8")
        run_ruff_format(init_path, module_dir)
        return init_path

    if not template_content.strip():
        return None

    current_content = init_path.read_text(encoding="utf-8")
    content = _merge_module_init_template_content(
        current=current_content,
        template_content=template_content,
        module_name=module_name,
    )
    if content == current_content:
        return None

    if dry_run:
        return init_path

    init_path.write_text(content, encoding="utf-8")
    run_ruff_format(init_path, module_dir)
    return init_path


def _build_module_template_context(
    *,
    module_name: str,
    has_controller: bool,
    has_entity: bool,
) -> dict[str, str | bool]:
    module_class_name = "".join(part.capitalize() for part in module_name.split("_") if part)
    return {
        "module_name": module_name,
        "module_class_name": module_class_name,
        "has_controller": has_controller,
        "has_entity": has_entity,
    }


def _render_module_init_template(
    *,
    use_folders: bool,
    context: dict[str, str | bool],
) -> str:
    template_dir = ROOT_DIR / "templates" / "add" / "module" / ("folder" if use_folders else "flat")
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(enabled_extensions=()),
        keep_trailing_newline=True,
    )
    template = env.get_template("__init__.py.j2")
    return template.render(**context)


def _merge_module_init_template_content(
    *,
    current: str,
    template_content: str,
    module_name: str,
) -> str:
    merged = current
    module_router_line = f"{module_name}_module_router = APIRouter()"

    for template_line in template_content.splitlines():
        line = template_line.strip()
        if not line:
            continue

        parsed_assignment = _parse_symbol_list_assignment(line)
        if parsed_assignment:
            list_name, symbol_names = parsed_assignment
            for symbol_name in symbol_names:
                merged = _merge_symbol_list_assignment(
                    current=merged,
                    list_name=list_name,
                    symbol_name=symbol_name,
                )
            continue

        if line.startswith(f"{module_name}_module_router.include_router("):
            merged = _merge_required_line(
                current=merged,
                required_line=line,
                anchor_line=module_router_line,
            )
            continue

        merged = _merge_required_line(current=merged, required_line=line)

    return merged


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


def _parse_symbol_list_assignment(line: str) -> tuple[str, list[str]] | None:
    assignment_match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\[(.*)]", line)
    if not assignment_match:
        return None

    list_name = assignment_match.group(1)
    raw_values = assignment_match.group(2)
    symbols = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", raw_values)
    return list_name, symbols


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
