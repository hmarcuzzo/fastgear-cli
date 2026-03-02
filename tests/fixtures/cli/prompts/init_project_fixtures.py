import pytest


@pytest.fixture
def valid_project_name() -> str:
    return "my-awesome-project"


@pytest.fixture
def project_name_with_underscores() -> str:
    return "my_awesome_project"


@pytest.fixture
def project_name_with_mixed_separators() -> str:
    return "my-awesome_project"
