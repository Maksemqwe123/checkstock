from datetime import datetime

from pydantic import BaseModel
from uuid import UUID

from checkstock_backend.api.schemas.ful_fillment_center import FulfillmentCenterModel
from checkstock_backend.api.schemas.product import ProductModel


class FboShipmentCreateModel(BaseModel):
    fulfillment_center: FulfillmentCenterModel
    product: ProductModel
    quantity: int

class FboShipmentModel(FboShipmentCreateModel):
    id: UUID
    accepted: bool
    created: datetime
    updated: datetime
