from typing import Annotated

import typer

from fastgear_cli import __version__
from fastgear_cli.cli.commands.add import add_app
from fastgear_cli.cli.commands.init import init_app

app = typer.Typer(help="Fastgear code generator", invoke_without_command=True)

app.add_typer(init_app)
app.add_typer(add_app)


@app.callback()
def main_callback(
    version: Annotated[
        bool | None,
        typer.Option("--version", "-v", is_eager=True, help="Show version and exit"),
    ] = None,
) -> None:
    if version:
        typer.echo(f"fg v{__version__}")
        raise typer.Exit


def main():
    app()


if __name__ == "__main__":
    main()
