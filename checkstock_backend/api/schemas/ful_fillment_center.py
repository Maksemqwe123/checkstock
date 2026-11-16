from datetime import datetime

from pydantic import BaseModel
from uuid import UUID


class FulfillmentCenterCreateModel(BaseModel):
    name: str
    code: str
    city: str
    address: str


class FulfillmentCenterModel(FulfillmentCenterCreateModel):
    id: UUID
    is_active: bool
    created: datetime
    updated: datetime

    model_config = {"from_attributes": True}
