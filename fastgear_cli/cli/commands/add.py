from collections.abc import Callable
from pathlib import Path

import typer

from fastgear_cli.cli.commands.helpers.add_controller_helper import (
    ask_service_path,
    handle_controller_files,
    validate_service_path,
)
from fastgear_cli.cli.commands.helpers.add_entity_helper import handle_entity_files
from fastgear_cli.cli.commands.helpers.add_module_helper import resolve_module_components
from fastgear_cli.cli.commands.helpers.add_repository_helper import (
    ask_entity_path,
    handle_repository_files,
    validate_entity_path,
)
from fastgear_cli.cli.commands.helpers.add_service_helper import (
    ask_repository_path,
    handle_service_files,
    validate_repository_path,
)
from fastgear_cli.core.constants.enums import ElementTypeEnum
from fastgear_cli.core.exceptions import FastgearCliError, InvalidInputError, TemplateConflictError
from fastgear_cli.core.filesystem import create_template
from fastgear_cli.core.models import AddElementConfig
from fastgear_cli.core.models.add_element_config import (
    normalize_element_name,
    parse_element_type,
)
from fastgear_cli.core.utils.file_tree_utils import FileTreeUtils

add_app = typer.Typer(help="Add new components to an existing FastGear project")

AddFileHandler = Callable[..., list[Path]]
ADD_FILE_HANDLERS: dict[ElementTypeEnum, AddFileHandler] = {
    ElementTypeEnum.CONTROLLER: handle_controller_files,
    ElementTypeEnum.ENTITY: handle_entity_files,
    ElementTypeEnum.REPOSITORY: handle_repository_files,
    ElementTypeEnum.SERVICE: handle_service_files,
}


@add_app.command()
def add(
    element_type: str = typer.Argument(
        ...,
        help="Element type: module | controller | service | entity | repository",
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
    entity_path: str | None = typer.Option(
        None,
        "--entity-path",
        help="Entity import path used by repository (e.g. src.modules.user.entities.User)",
    ),
    repository_path: str | None = typer.Option(
        None,
        "--repository-path",
        help="Repository import path used by service (optional, e.g. src.modules.user.repositories.user_repository.UserRepository)",
    ),
    service_path: str | None = typer.Option(
        None,
        "--service-path",
        help="Service import path used by controller (optional, e.g. src.modules.user.services.user_service.UserService)",
    ),
    module_components: str | None = typer.Option(
        None,
        "--module-components",
        help="Comma-separated components for module: controller,service,repository,entity (if omitted, asks interactively)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what files would be created without actually creating them",
    ),
) -> None:
    try:
        resolved_element_type = parse_element_type(element_type)
        resolved_element_name = normalize_element_name(element_name)
        base_dir = path or Path.cwd()

        if resolved_element_type == ElementTypeEnum.MODULE:
            files = _add_module(
                base_dir=base_dir,
                module_name=resolved_element_name,
                use_folders=use_folders,
                entity_path=entity_path,
                repository_path=repository_path,
                service_path=service_path,
                module_components=module_components,
                dry_run=dry_run,
            )
            output_base_dir = base_dir
            success_message = f"\nAdded module {resolved_element_name} successfully!"
        else:
            if module_components is not None:
                raise InvalidInputError(
                    "--module-components can only be used with element type module."
                )

            resolved_entity_path, resolved_repository_path, resolved_service_path = _resolve_paths(
                element_type=resolved_element_type,
                entity_path=entity_path,
                repository_path=repository_path,
                service_path=service_path,
            )
            config = AddElementConfig(
                base_dir=base_dir,
                element_type=resolved_element_type,
                element_name=resolved_element_name,
                use_folders=use_folders,
                entity_path=resolved_entity_path,
                repository_path=resolved_repository_path,
                service_path=resolved_service_path,
            )
            files = _create_component_files(config, dry_run=dry_run)
            output_base_dir = config.base_dir
            success_message = f"\nAdded {config.element_type} successfully!"

        if dry_run:
            FileTreeUtils.display_dry_run_output(files, output_base_dir)
            return

        typer.secho(success_message, fg=typer.colors.GREEN)
    except FastgearCliError as error:
        typer.secho(str(error), fg=typer.colors.RED)
        raise typer.Exit(code=1) from error


def _add_module(
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
    components = resolve_module_components(module_components)
    selected_components = set(components)
    module_import_root = _resolve_module_import_root(base_dir=base_dir, module_name=module_name)
    created_files: list[Path] = []

    module_init = module_dir / "__init__.py"
    if not module_init.exists():
        if not dry_run:
            module_init.parent.mkdir(parents=True, exist_ok=True)
            module_init.write_text("", encoding="utf-8")
        created_files.append(module_init)

    for component in components:
        resolved_entity_path, resolved_repository_path, resolved_service_path = (
            _resolve_module_paths(
                component=component,
                module_name=module_name,
                selected_components=selected_components,
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
            component_files = _create_component_files(config, dry_run=dry_run)
        except TemplateConflictError:
            continue
        _append_unique_files(created_files, component_files)

    if not created_files:
        raise TemplateConflictError("No new files created. The content may already exist.")

    return created_files


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
                module_name=module_name,
                module_class_name=module_class_name,
                module_import_root=module_import_root,
                use_folders=use_folders,
            )

    if component == ElementTypeEnum.SERVICE:
        if resolved_repository_path is not None:
            resolved_repository_path = validate_repository_path(resolved_repository_path)
        elif ElementTypeEnum.REPOSITORY in selected_components:
            resolved_repository_path = _build_module_repository_path(
                module_name=module_name,
                module_class_name=module_class_name,
                module_import_root=module_import_root,
                use_folders=use_folders,
            )

    if component == ElementTypeEnum.CONTROLLER:
        if resolved_service_path is not None:
            resolved_service_path = validate_service_path(resolved_service_path)
        elif ElementTypeEnum.SERVICE in selected_components:
            resolved_service_path = _build_module_service_path(
                module_name=module_name,
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
    module_name: str,
    module_class_name: str,
    module_import_root: str,
    use_folders: bool,
) -> str:
    if use_folders:
        return f"{module_import_root}.entities.{module_class_name}"
    return f"{module_import_root}.{module_class_name}"


def _build_module_repository_path(
    *,
    module_name: str,
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
    module_name: str,
    module_class_name: str,
    module_import_root: str,
    use_folders: bool,
) -> str:
    service_class_name = f"{module_class_name}Service"
    if use_folders:
        return f"{module_import_root}.services.{service_class_name}"
    return f"{module_import_root}.{service_class_name}"


def _create_component_files(config: AddElementConfig, *, dry_run: bool) -> list[Path]:
    files = create_template(
        f"add/{config.element_type}/{config.structure}",
        config.base_dir,
        config.context,
        dry_run=dry_run,
    )

    handler = ADD_FILE_HANDLERS.get(config.element_type)
    if handler:
        files = handler(config, dry_run=dry_run, files=files)

    return files


def _append_unique_files(base_files: list[Path], new_files: list[Path]) -> None:
    for file_path in new_files:
        if file_path not in base_files:
            base_files.append(file_path)


def _resolve_paths(
    *,
    element_type: ElementTypeEnum,
    entity_path: str | None,
    repository_path: str | None,
    service_path: str | None,
) -> tuple[str | None, str | None, str | None]:
    resolved_entity_path = entity_path
    resolved_repository_path = repository_path
    resolved_service_path = service_path

    if element_type == ElementTypeEnum.REPOSITORY and resolved_entity_path is None:
        resolved_entity_path = ask_entity_path()
    elif element_type == ElementTypeEnum.REPOSITORY:
        resolved_entity_path = validate_entity_path(resolved_entity_path)

    if element_type == ElementTypeEnum.SERVICE and resolved_repository_path is None:
        resolved_repository_path = ask_repository_path()
    elif element_type == ElementTypeEnum.SERVICE:
        resolved_repository_path = validate_repository_path(resolved_repository_path)

    if element_type == ElementTypeEnum.CONTROLLER and resolved_service_path is None:
        resolved_service_path = ask_service_path()
    elif element_type == ElementTypeEnum.CONTROLLER:
        resolved_service_path = validate_service_path(resolved_service_path)

    return resolved_entity_path, resolved_repository_path, resolved_service_path
