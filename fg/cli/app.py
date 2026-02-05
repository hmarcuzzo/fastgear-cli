import typer

from fg.cli.commands.init import init_app

app = typer.Typer(help="Fastgear code generator")

app.add_typer(init_app)


def main():
    app()


if __name__ == "__main__":
    main()
