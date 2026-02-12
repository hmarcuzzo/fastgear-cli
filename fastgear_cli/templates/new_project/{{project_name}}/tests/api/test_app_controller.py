import pytest
from httpx import AsyncClient


@pytest.mark.describe("🧪  AppController")
class TestAppController:
    @pytest.mark.it("✅  Should return health status ok")
    @pytest.mark.anyio
    async def test_health_returns_ok_status(self, async_client: AsyncClient):
        response = await async_client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
