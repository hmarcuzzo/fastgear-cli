from pathlib import Path

from fg.configs.settings import ROOT_DIR
from fg.core.render import render_template_dir


def create_project(template_name: str, context: dict) -> None:
    template_root = ROOT_DIR / "templates" / template_name
    render_template_dir(template_root, Path.cwd(), context)
