from datetime import datetime

from pydantic import BaseModel
from uuid import UUID

from checkstock_backend.api.schemas.ful_fillment_center import FulfillmentCenterModel
from checkstock_backend.api.schemas.product import ProductModel

from checkstock_backend.db.models.fbs import FbsOrderStatus

from typing import Optional


class FbsOrderCreateModel(BaseModel):
    fulfillment_center: FulfillmentCenterModel
    product: ProductModel
    quantity: Optional[int] = None

class FbsOrderModel(FbsOrderCreateModel):
    id: UUID
    status: FbsOrderStatus
    created: datetime
    updated: datetime


class FbsReservationLineCreateModel(BaseModel):
    order: FbsOrderModel
    fulfillment_center: FulfillmentCenterModel
    quantity: Optional[int] = None

class FbsReservationLineModel(FbsReservationLineCreateModel):
    id: UUID
    created: datetime
    updated: datetime