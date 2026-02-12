import pytest
from src.modules.app.app_service import AppService


@pytest.mark.describe("🧪  AppService")
class TestAppService:
    @pytest.mark.it("✅  Should return health status ok")
    def test_health_returns_ok_status(self):
        result = AppService.health()

        assert result == {"status": "ok"}
