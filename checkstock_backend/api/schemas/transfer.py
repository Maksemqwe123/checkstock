from datetime import datetime

from pydantic import BaseModel
from uuid import UUID

from checkstock_backend.api.schemas.ful_fillment_center import FulfillmentCenterModel
from checkstock_backend.api.schemas.product import ProductModel

from checkstock_backend.db.models.transfer import TransferStatus


class TransferCreateModel(BaseModel):
    from_ff: FulfillmentCenterModel
    to_ff: FulfillmentCenterModel
    product: ProductModel
    quantity: int


class TransferModel(TransferCreateModel):
    id: UUID
    status: TransferStatus
    created: datetime
    updated: datetime
