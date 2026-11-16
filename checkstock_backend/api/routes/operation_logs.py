from typing import List

from fastapi import APIRouter, Query

from checkstock_backend.api.schemas.operation_log import OperationLogModel
from checkstock_backend.api.utils import queries

router = APIRouter()


@router.get(
    "",
    summary="Журнал операций",
    status_code=200,
    response_model=List[OperationLogModel],
)
async def list_operations(limit: int = Query(100, ge=1, le=500)):
    return await queries.operation_history(limit)