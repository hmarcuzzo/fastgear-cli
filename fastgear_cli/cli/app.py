import typer

from fastgear_cli.cli.commands.add import add_app
from fastgear_cli.cli.commands.init import init_app

app = typer.Typer(help="Fastgear code generator")

app.add_typer(init_app)
app.add_typer(add_app)


def main():
    app()


if __name__ == "__main__":
    main()
