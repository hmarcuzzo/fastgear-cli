import pytest

from tests.fixtures.api_fixture import async_client  # noqa: F401


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"
