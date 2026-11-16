from typing import List

from fastapi import APIRouter

from checkstock_backend.api.schemas.responses import StockInTransitOut
from checkstock_backend.db.models.stock_in_transit import StockInTransit

router = APIRouter()


@router.get(
    "",
    summary="Товары в пути",
    status_code=200,
    response_model=List[StockInTransitOut],
)
async def list_in_transit():
    return await StockInTransit.all().order_by("-created")