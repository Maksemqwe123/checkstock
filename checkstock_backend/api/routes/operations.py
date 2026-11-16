from fastapi import APIRouter, Header

from checkstock_backend.api.schemas.requests import OperationKind, OperationRequest
from checkstock_backend.api.schemas.responses import (
    FboShipmentOut,
    FbsOrderOut,
    OperationResponse,
    StockBalanceOut,
    TransferOut,
)
from checkstock_backend.api.utils.http import http_error, merge_idempotency
from checkstock_backend.api.utils.inventory import InventoryService

router = APIRouter()
svc = InventoryService()


def _balance_out(bal) -> StockBalanceOut:
    return StockBalanceOut(
        id=bal.id,
        fulfillment_center_id=bal.fulfillment_center_id,
        product_id=bal.product_id,
        physical_qty=bal.physical_qty,
        reserved_fbs_qty=bal.reserved_fbs_qty,
        available=bal.physical_qty - bal.reserved_fbs_qty,
        created=bal.created,
        updated=bal.updated,
    )


@router.post(
    "",
    response_model=OperationResponse,
    summary="Операция учёта (type: arrival, transfer_ship, …)",
)
async def perform_operation(
    body: OperationRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    key = merge_idempotency(body.idempotency_key, idempotency_key)
    try:
        if body.type == OperationKind.arrival:
            bal = await svc.arrival(
                body.fulfillment_center_id,
                body.product_id,
                body.quantity,
                key,
            )
            return OperationResponse(
                type=body.type.value,
                stock_balance=_balance_out(bal),
            )

        if body.type == OperationKind.transfer_ship:
            transfer = await svc.ship_transfer(
                body.from_ff_id,
                body.to_ff_id,
                body.product_id,
                body.quantity,
                key,
            )
            return OperationResponse(type=body.type.value, transfer=TransferOut.model_validate(transfer))

        if body.type == OperationKind.transfer_receive:
            transfer = await svc.receive_transfer(body.transfer_id, key)
            return OperationResponse(type=body.type.value, transfer=TransferOut.model_validate(transfer))

        if body.type == OperationKind.fbs_reserve:
            order = await svc.reserve_fbs(
                body.fulfillment_center_id,
                body.product_id,
                body.quantity,
                body.allow_cross_ff,
                key,
            )
            return OperationResponse(type=body.type.value, fbs_order=FbsOrderOut.model_validate(order))

        if body.type == OperationKind.fbs_ship:
            order = await svc.ship_fbs(body.order_id, key)
            return OperationResponse(type=body.type.value, fbs_order=FbsOrderOut.model_validate(order))

        if body.type == OperationKind.fbs_cancel:
            order = await svc.cancel_fbs(body.order_id, key)
            return OperationResponse(type=body.type.value, fbs_order=FbsOrderOut.model_validate(order))

        if body.type == OperationKind.fbo_ship:
            shipment = await svc.ship_fbo(
                body.fulfillment_center_id,
                body.product_id,
                body.quantity,
                key,
            )
            return OperationResponse(type=body.type.value, fbo_shipment=FboShipmentOut.model_validate(shipment))

        if body.type == OperationKind.fbo_accept:
            shipment = await svc.accept_fbo(body.shipment_id, key)
            return OperationResponse(type=body.type.value, fbo_shipment=FboShipmentOut.model_validate(shipment))
    except Exception as e:
        raise http_error(e) from e