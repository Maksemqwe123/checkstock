from checkstock_backend.db.models.ful_fillment_center import FulfillmentCenter
from checkstock_backend.db.models.operation_log import OperationLog
from checkstock_backend.db.models.product import Product
from checkstock_backend.db.models.stock_balance import StockBalance
from checkstock_backend.db.models.stock_in_transit import StockInTransit, StockInTransitType


async def inventory_snapshot() -> dict:
    products = await Product.filter(is_active=True).order_by("sku")
    ffs = await FulfillmentCenter.all().order_by("created")
    balances = await StockBalance.all().prefetch_related("fulfillment_center", "product")
    by_key = {(b.fulfillment_center_id, b.product_id): b for b in balances}

    rows: list[dict] = []
    for p in products:
        for ff in ffs:
            b = by_key.get((ff.id, p.id))
            physical = b.physical_qty if b else 0
            reserved = b.reserved_fbs_qty if b else 0
            if physical == 0 and reserved == 0 and not ff.is_active:
                continue
            rows.append(
                {
                    "sku": p.sku,
                    "product_name": p.name,
                    "product_id": str(p.id),
                    "fulfillment_center_id": str(ff.id),
                    "fulfillment_center_name": ff.name if ff.is_active else f"{ff.name} (закрыт)",
                    "ff_active": ff.is_active,
                    "physical": physical,
                    "reserved_fbs": reserved,
                    "available": physical - reserved,
                }
            )

    in_transit = await StockInTransit.all().prefetch_related(
        "product", "fulfillment_center_from", "fulfillment_center_to"
    )
    kind_map = {
        StockInTransitType.BETWEEN_FF.value: "Между ФФ",
        StockInTransitType.TO_FBO.value: "На склад FBO",
        StockInTransitType.TO_FBS_CUSTOMER.value: "К клиенту (FBS)",
    }
    transit_rows = []
    for t in in_transit:
        product = t.product
        if not isinstance(product, Product):
            product = await t.product
        ff_from = t.fulfillment_center_from
        if ff_from is not None and not isinstance(ff_from, FulfillmentCenter):
            ff_from = await ff_from
        ff_to = t.fulfillment_center_to
        if ff_to is not None and not isinstance(ff_to, FulfillmentCenter):
            ff_to = await ff_to
        transit_rows.append(
            {
                "sku": product.sku if product else "?",
                "quantity": t.quantity,
                "kind": kind_map.get(t.transit_type, t.transit_type),
                "from_ff": _lbl(ff_from),
                "to_ff": _lbl(ff_to),
            }
        )

    return {"balances": rows, "in_transit": transit_rows}


def _lbl(ff: FulfillmentCenter | None) -> str:
    if not ff:
        return "—"
    return ff.name if ff.is_active else f"{ff.name} (закрыт)"


async def operation_history(limit: int = 100) -> list[OperationLog]:
    return await OperationLog.all().order_by("-created").limit(limit)