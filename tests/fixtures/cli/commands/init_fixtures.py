from pathlib import Path

import pytest


@pytest.fixture
def temp_directory(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def project_name() -> str:
    return "test-project"


@pytest.fixture
def project_title() -> str:
    return "Test Project"
