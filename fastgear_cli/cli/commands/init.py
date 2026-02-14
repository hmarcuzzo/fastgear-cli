import subprocess
from pathlib import Path

import typer

from fastgear_cli.cli.prompts.project import (
    ask_agent_tools,
    ask_project_name,
    confirm_project_title,
)
from fastgear_cli.core.filesystem import create_project
from fastgear_cli.core.models import ProjectInitConfig

init_app = typer.Typer(help="Project initialization command")


@init_app.command()
def init(
    directory: Path = typer.Argument(
        None,
        help="Directory where the project should be created (defaults to current directory)",
        exists=False,
    ),
):
    """
    Initialize a new project using fastgear.
    """
    base_dir = directory if directory else Path.cwd()

    project_name = ask_project_name()
    project_title = confirm_project_title(project_name)
    use_docker = typer.confirm("Use Docker?", default=True)
    agent_tools = ask_agent_tools()

    config = ProjectInitConfig(
        base_dir=base_dir,
        project_name=project_name,
        project_title=project_title,
        use_docker=use_docker,
        agent_tools=agent_tools,
    )

    try:
        create_project(
            "new_project",
            config.base_dir,
            config.context,
            config.conditional_files,
            config.conditional_dirs,
        )

    except FileExistsError:
        typer.secho(
            f"Directory '{config.project_dir}' already exists.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    typer.secho("📦 Generating uv.lock...", fg=typer.colors.CYAN)
    try:
        subprocess.run(
            ["uv", "lock"],
            cwd=config.project_dir,
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

    typer.secho(
        f"\n🎉  Project '{config.project_name}' created successfully!",
        fg=typer.colors.GREEN,
    )
