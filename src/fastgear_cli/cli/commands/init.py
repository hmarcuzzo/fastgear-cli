import typer

from fastgear_cli.cli.prompts.project import ask_project_name
from fastgear_cli.core.filesystem import create_project_structure
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
        create_project_structure(config.project_dir)
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
