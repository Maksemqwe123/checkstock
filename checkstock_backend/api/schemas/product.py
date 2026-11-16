from datetime import datetime

from pydantic import BaseModel
from uuid import UUID


class ProductCreateModel(BaseModel):
    sku: str
    name: str
    description: str | None = None


class ProductModel(ProductCreateModel):
    id: UUID
    is_active: bool
    created: datetime
    updated: datetime

    model_config = {"from_attributes": True}
