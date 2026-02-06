from pydantic import BaseModel


class HealthSchema(BaseModel):
    status: str
