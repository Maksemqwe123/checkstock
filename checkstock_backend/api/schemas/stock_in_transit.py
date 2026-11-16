from datetime import datetime

from pydantic import BaseModel
from uuid import UUID

from checkstock_backend.api.schemas.ful_fillment_center import FulfillmentCenterModel
from checkstock_backend.api.schemas.product import ProductModel
from checkstock_backend.api.schemas.transfer import TransferModel
from checkstock_backend.api.schemas.fbs import FbsOrderModel
from checkstock_backend.api.schemas.fbo_shopment import FboShipmentModel
from checkstock_backend.db.models.stock_in_transit import StockInTransitType

from typing import Optional


class StockInTransitCreateModel(BaseModel):
    product: ProductModel
    quantity: Optional[int] = None
    transit_type: StockInTransitType
    fulfillment_center_from: FulfillmentCenterModel
    fulfillment_center_to: FulfillmentCenterModel
    transfer: Optional[TransferModel] = None
    fbs_order: Optional[FbsOrderModel] = None
    fbo_shipment: Optional[FboShipmentModel] = None

class StockInTransitModel(StockInTransitCreateModel):
    id: UUID
    created: datetime
    updated: datetime