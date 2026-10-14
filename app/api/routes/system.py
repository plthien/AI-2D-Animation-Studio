from fastapi import APIRouter
from app.api.schemas.base import DataEnvelope, HealthResponse

router = APIRouter()


@router.get("/health", response_model=DataEnvelope[HealthResponse])
def health() -> dict:
    return {"data": {"status": "ok", "schema_version": "1"}}
