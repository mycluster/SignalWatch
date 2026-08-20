"""Pipeline observability API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from signalwatch.api.schemas.pipeline import PipelineHealthResponse
from signalwatch.api.services.pipeline_service import PipelineService

router = APIRouter(tags=["pipeline"])


def get_pipeline_service() -> PipelineService:
    """Return pipeline service dependency."""
    return PipelineService()


PIPELINE_SERVICE_DEPENDENCY = Depends(get_pipeline_service)


@router.get("/pipeline/health", response_model=PipelineHealthResponse)
async def pipeline_health(
    pipeline_service: PipelineService = PIPELINE_SERVICE_DEPENDENCY,
) -> PipelineHealthResponse:
    """Return latest ingestion/normalization pipeline status."""
    return PipelineHealthResponse.model_validate(pipeline_service.get_health())
