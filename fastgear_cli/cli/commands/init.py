import typer

from fastgear_cli.cli.prompts.project import ask_project_name
from fastgear_cli.core.filesystem import create_project
from fastgear_cli.core.models import ProjectInitConfig

init_app = typer.Typer(help="Project initialization command")


@init_app.command()
def init():
    """
    Initialize a new project using fastgear.
    """
    project_name = ask_project_name()

    config = ProjectInitConfig(name=project_name)

    try:
        context = {
            "project_name": config.name,
            "project_title": config.name.title(),
            "use_docker": True,
        }
        conditional_files = {
            ".dockerignore": context["use_docker"],
        }
        conditional_dirs = {
            "docker": context["use_docker"],
        }

        create_project("default_project", context, conditional_files, conditional_dirs)
    except FileExistsError:
        typer.secho(
            f"Directory '{config.project_dir}' already exists.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    typer.secho(
        f"Project '{config.name}' created successfully.",
        fg=typer.colors.GREEN,
    )
