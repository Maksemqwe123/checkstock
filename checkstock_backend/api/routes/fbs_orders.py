from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException

from checkstock_backend.api.schemas.responses import FbsOrderOut
from checkstock_backend.db.models.fbs import FbsOrder

router = APIRouter()


@router.get(
    "",
    summary="Заказы FBS",
    status_code=200,
    response_model=List[FbsOrderOut],
)
async def list_orders():
    return await FbsOrder.all().order_by("-created")


@router.get(
    "/{order_id}",
    summary="Заказ FBS по ID",
    status_code=200,
    response_model=FbsOrderOut,
)
async def get_order(order_id: UUID):
    order = await FbsOrder.get_or_none(id=order_id)
    if order is None:
        raise HTTPException(404, detail="Заказ FBS не найден")
    return order