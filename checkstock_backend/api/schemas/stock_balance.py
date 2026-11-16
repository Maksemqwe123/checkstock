from datetime import datetime

from pydantic import BaseModel
from uuid import UUID

from checkstock_backend.api.schemas.ful_fillment_center import FulfillmentCenterModel
from checkstock_backend.api.schemas.product import ProductModel


class StockBalanceCreateModel(BaseModel):
    fulfillment_center: FulfillmentCenterModel
    product: ProductModel
    physical_qty: int
    reserved_fbs_qty: int


class StockBalanceModel(StockBalanceCreateModel):
    id: UUID
    created: datetime
    updated: datetime
