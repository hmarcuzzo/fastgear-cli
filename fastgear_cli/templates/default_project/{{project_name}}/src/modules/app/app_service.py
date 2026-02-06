from typing import cast

from src.modules.app.app_schemas import HealthSchema


class AppService:
    @staticmethod
    def health() -> HealthSchema:
        return cast(
            "HealthSchema",
            {"status": "ok"},
        )
