from fastapi import APIRouter
from src.modules.app.app_controller import app_router
from src.modules.domain import domain_routers

app_routers = APIRouter()

# Include App Modules Routes
app_routers.include_router(app_router)
app_routers.include_router(domain_routers)
