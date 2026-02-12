from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient]:
    base_url = "http://test"
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url=base_url) as async_client:
        yield async_client
