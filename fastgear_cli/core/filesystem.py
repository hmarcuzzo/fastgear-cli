from pathlib import Path

import typer

from fastgear_cli.configs.settings import ROOT_DIR
from fastgear_cli.core.render import render_template


def create_project(
    template_name: str,
    base_dir: Path,
    context: dict,
    conditional_files: dict[str, bool] | None = None,
    conditional_dirs: dict[str, bool] | None = None,
    *,
    dry_run: bool = False,
) -> list[Path]:
    conditional_files = conditional_files or {}
    conditional_dirs = conditional_dirs or {}

    template_root = ROOT_DIR / "templates" / template_name
    files = render_template(
        template_root,
        base_dir,
        context,
        conditional_files,
        conditional_dirs,
        dry_run=dry_run,
    )

    if not files:
        typer.secho(
            "\nNo new files created. The content may already exist.",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(code=1)

    return files
