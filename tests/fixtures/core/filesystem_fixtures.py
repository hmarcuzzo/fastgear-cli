from pathlib import Path

import pytest


@pytest.fixture
def temp_directory(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def template_directory(tmp_path: Path) -> Path:
    template_dir = tmp_path / "templates" / "test_template"
    template_dir.mkdir(parents=True)
    return template_dir


@pytest.fixture
def output_directory(tmp_path: Path) -> Path:
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True)
    return output_dir


@pytest.fixture
def sample_context() -> dict:
    return {
        "project_name": "my-project",
        "project_title": "My Project",
        "use_docker": True,
    }


@pytest.fixture
def template_with_files(template_directory: Path) -> Path:
    (template_directory / "{{project_name}}").mkdir()
    (template_directory / "{{project_name}}" / "README.md.j2").write_text("# {{ project_title }}\n")
    (template_directory / "{{project_name}}" / "config.txt").write_text("static content")
    return template_directory


@pytest.fixture
def template_with_conditional_dir(template_directory: Path) -> Path:
    (template_directory / "{{project_name}}").mkdir()
    docker_dir = template_directory / "{{project_name}}" / "docker"
    docker_dir.mkdir()
    (docker_dir / "Dockerfile").write_text("FROM python:3.11")
    (template_directory / "{{project_name}}" / "src").mkdir()
    (template_directory / "{{project_name}}" / "src" / "main.py").write_text("print('hello')")
    return template_directory


@pytest.fixture
def template_with_conditional_file(template_directory: Path) -> Path:
    project_dir = template_directory / "{{project_name}}"
    project_dir.mkdir()
    (project_dir / "README.md").write_text("# README")
    (project_dir / "OPTIONAL.md").write_text("# Optional file")
    return template_directory
