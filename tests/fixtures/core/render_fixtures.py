from pathlib import Path

import pytest


@pytest.fixture
def template_root(tmp_path: Path) -> Path:
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    return template_dir


@pytest.fixture
def output_root(tmp_path: Path) -> Path:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def simple_context() -> dict:
    return {
        "project_name": "my-project",
        "project_title": "My Project",
    }


@pytest.fixture
def template_with_jinja2_file(template_root: Path) -> Path:
    readme = template_root / "README.md.j2"
    readme.write_text("# {{ project_title }}\n\nProject: {{ project_name }}")
    return template_root


@pytest.fixture
def template_with_static_file(template_root: Path) -> Path:
    static_file = template_root / "static.txt"
    static_file.write_text("This is static content")
    return template_root


@pytest.fixture
def template_with_nested_dirs(template_root: Path) -> Path:
    nested_dir = template_root / "{{project_name}}" / "src"
    nested_dir.mkdir(parents=True)
    (nested_dir / "main.py.j2").write_text("# {{ project_title }}")
    return template_root


@pytest.fixture
def template_with_conditional_dir(template_root: Path) -> Path:
    project_dir = template_root / "project"
    project_dir.mkdir()
    docker_dir = project_dir / "docker"
    docker_dir.mkdir()
    (docker_dir / "Dockerfile").write_text("FROM python:3.11")
    src_dir = project_dir / "src"
    src_dir.mkdir()
    (src_dir / "app.py").write_text("print('app')")
    return template_root


@pytest.fixture
def template_with_conditional_file(template_root: Path) -> Path:
    (template_root / "README.md").write_text("# README")
    (template_root / ".dockerignore").write_text("*.pyc")
    return template_root
