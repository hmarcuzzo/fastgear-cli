from pathlib import Path

import pytest


@pytest.fixture
def temp_directory(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def valid_project_name() -> str:
    return "my-project"


@pytest.fixture
def valid_project_title() -> str:
    return "My Project"


@pytest.fixture
def project_config_data(temp_directory: Path) -> dict:
    return {
        "base_dir": temp_directory,
        "project_name": "test-project",
        "project_title": "Test Project",
        "use_docker": True,
    }


@pytest.fixture
def project_config_without_docker(temp_directory: Path) -> dict:
    return {
        "base_dir": temp_directory,
        "project_name": "test-project",
        "project_title": "Test Project",
        "use_docker": False,
    }
