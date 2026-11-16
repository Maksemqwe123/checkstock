from datetime import datetime

from pydantic import BaseModel
from uuid import UUID

from typing import Optional


class OperationLogModel(BaseModel):
    id: UUID
    operation_type: str
    description: str
    idempotency_key: str | None = None
    payload_json: str | None = None
    created: datetime

    model_config = {"from_attributes": True}
