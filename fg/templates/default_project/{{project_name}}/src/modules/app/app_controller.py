from fastapi import APIRouter
from fastgear.decorators import controller
from src.modules.app.app_schemas import HealthSchema
from src.modules.app.app_service import AppService

app_router = APIRouter(tags=["App"])


@controller(app_router)
class AppController:
    def __init__(self):
        self.app_service = AppService()

    @app_router.get("/health")
    def health(self) -> HealthSchema:
        return self.app_service.health()
