from pathlib import Path

from fastgear_cli.configs.settings import ROOT_DIR
from fastgear_cli.core.render import render_template_dir


def create_project(template_name: str, context: dict, conditional_files: dict) -> None:
    template_root = ROOT_DIR / "templates" / template_name
    render_template_dir(template_root, Path.cwd(), context, conditional_files)
