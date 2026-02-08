from pathlib import Path

import typer

from fastgear_cli.cli.prompts.project import ask_project_name, confirm_project_title
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

    config = ProjectInitConfig(
        base_dir=base_dir,
        project_name=project_name,
        project_title=project_title,
        use_docker=use_docker,
    )

    try:
        context = {
            "project_name": config.project_name,
            "project_title": config.project_title,
            "use_docker": config.use_docker,
        }
        conditional_files = {
            ".dockerignore": context["use_docker"],
        }
        conditional_dirs = {
            "docker": context["use_docker"],
        }

        create_project(
            "new_project",
            config.base_dir,
            context,
            conditional_files,
            conditional_dirs,
        )
    except FileExistsError:
        typer.secho(
            f"Directory '{config.project_dir}' already exists.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    typer.secho(
        f"\n🎉  Project '{config.project_name}' created successfully!",
        fg=typer.colors.GREEN,
    )
