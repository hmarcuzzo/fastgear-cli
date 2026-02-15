import subprocess
from pathlib import Path

import questionary
import typer

from fastgear_cli.cli.prompts.project import (
    ask_agent_tools,
    ask_ci_provider,
    ask_project_name,
    confirm_project_title,
)
from fastgear_cli.core.filesystem import create_project
from fastgear_cli.core.models import ProjectInitConfig
from fastgear_cli.core.utils.file_tree_utils import FileTreeUtils

init_app = typer.Typer(help="Project initialization command")


@init_app.command()
def init(
    directory: Path = typer.Argument(
        None,
        help="Directory where the project should be created (defaults to current directory)",
        exists=False,
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what files would be created without actually creating them",
    ),
):
    base_dir = directory if directory else Path.cwd()

    config = _collect_project_info(base_dir)
    files = _generate_project(config, dry_run=dry_run)

    if dry_run:
        _display_dry_run_output(files, base_dir)
        return

    _run_uv_lock(config.project_dir)

    typer.secho(
        f"\n🎉  Project '{config.project_name}' created successfully!",
        fg=typer.colors.GREEN,
    )


def _collect_project_info(base_dir: Path) -> ProjectInitConfig:
    project_name = ask_project_name()
    project_title = confirm_project_title(project_name)
    use_docker = questionary.confirm("Use Docker?", default=True).ask()
    agent_tools = ask_agent_tools()
    ci_provider = ask_ci_provider()

    return ProjectInitConfig(
        base_dir=base_dir,
        project_name=project_name,
        project_title=project_title,
        use_docker=use_docker,
        agent_tools=agent_tools,
        ci_provider=ci_provider,
    )


def _generate_project(config: ProjectInitConfig, *, dry_run: bool) -> list[Path]:
    try:
        return create_project(
            "new_project",
            config.base_dir,
            config.context,
            config.conditional_files,
            config.conditional_dirs,
            dry_run=dry_run,
        )
    except FileExistsError:
        typer.secho(
            f"Directory '{config.project_dir}' already exists.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)


def _display_dry_run_output(files: list[Path], base_dir: Path) -> None:
    typer.secho("\n🔍 Dry run mode - no files created\n", fg=typer.colors.YELLOW)
    typer.secho("Files that would be created:", fg=typer.colors.CYAN)
    FileTreeUtils.print_file_tree(files, base_dir)
    typer.secho(f"\nTotal: {len(files)} file(s)", fg=typer.colors.CYAN)


def _run_uv_lock(project_dir: Path) -> None:
    typer.secho("📦 Generating uv.lock...", fg=typer.colors.CYAN)
    try:
        subprocess.run(
            ["uv", "lock"],
            cwd=project_dir,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        typer.secho(
            f"Failed to generate uv.lock: {error.stderr}",
            fg=typer.colors.YELLOW,
        )
    except FileNotFoundError:
        typer.secho(
            "uv not found. Please install uv to generate the lock file.",
            fg=typer.colors.YELLOW,
        )
