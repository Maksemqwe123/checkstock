from fastapi import APIRouter

from checkstock_backend.api.utils import queries

router = APIRouter()


@router.get(
    "/snapshot",
    summary="Остатки и в пути (экран 01)",
    status_code=200,
)
async def snapshot():
    return await queries.inventory_snapshot()


@router.get(
    "/sku-totals",
    summary="Итого по SKU",
    status_code=200,
)
async def sku_totals():
    return await queries.sku_totals()