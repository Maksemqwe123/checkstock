from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StockBalanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    fulfillment_center_id: UUID
    product_id: UUID
    physical_qty: int
    reserved_fbs_qty: int
    available: int = 0
    created: datetime
    updated: datetime


class TransferOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    from_ff_id: UUID
    to_ff_id: UUID
    product_id: UUID
    quantity: int
    status: str
    created: datetime
    updated: datetime


class FbsOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    fulfillment_center_id: UUID
    product_id: UUID
    quantity: int
    status: str
    created: datetime
    updated: datetime


class FboShipmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    fulfillment_center_id: UUID
    product_id: UUID
    quantity: int
    accepted: bool
    created: datetime
    updated: datetime


class OperationResponse(BaseModel):
    type: str
    stock_balance: StockBalanceOut | None = None
    transfer: TransferOut | None = None
    fbs_order: FbsOrderOut | None = None
    fbo_shipment: FboShipmentOut | None = None


class StockInTransitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    quantity: int
    transit_type: str
    fulfillment_center_from_id: UUID | None
    fulfillment_center_to_id: UUID | None
    transfer_id: UUID | None
    fbs_order_id: UUID | None
    fbo_shipment_id: UUID | None
    created: datetime