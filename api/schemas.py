from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class ModelInfo(BaseModel):
    configured: bool
    loaded: bool
    message: str
