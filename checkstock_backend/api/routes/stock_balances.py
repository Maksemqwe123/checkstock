from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException

from checkstock_backend.api.schemas.responses import StockBalanceOut
from checkstock_backend.db.models.stock_balance import StockBalance

router = APIRouter()


def _out(b: StockBalance) -> StockBalanceOut:
    return StockBalanceOut(
        id=b.id,
        fulfillment_center_id=b.fulfillment_center_id,
        product_id=b.product_id,
        physical_qty=b.physical_qty,
        reserved_fbs_qty=b.reserved_fbs_qty,
        available=b.physical_qty - b.reserved_fbs_qty,
        created=b.created,
        updated=b.updated,
    )


@router.get(
    "",
    summary="Остатки по ФФ и товарам",
    status_code=200,
    response_model=List[StockBalanceOut],
)
async def list_balances():
    rows = await StockBalance.all().order_by("created")
    return [_out(b) for b in rows]


@router.get(
    "/{balance_id}",
    summary="Остаток по ID",
    status_code=200,
    response_model=StockBalanceOut,
)
async def get_balance(balance_id: UUID):
    b = await StockBalance.get_or_none(id=balance_id)
    if b is None:
        raise HTTPException(404, detail="Запись остатка не найдена")
    return _out(b)