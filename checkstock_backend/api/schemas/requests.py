from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class IdempotencyMixin(BaseModel):
    idempotency_key: str | None = None


class OperationKind(str, Enum):
    arrival = "arrival"
    transfer_ship = "transfer_ship"
    transfer_receive = "transfer_receive"
    fbs_reserve = "fbs_reserve"
    fbs_ship = "fbs_ship"
    fbs_cancel = "fbs_cancel"
    fbo_ship = "fbo_ship"
    fbo_accept = "fbo_accept"


class OperationRequest(IdempotencyMixin):
    """Одна ручка: поле type + параметры нужного сценария."""

    type: OperationKind
    fulfillment_center_id: UUID | None = None
    product_id: UUID | None = None
    quantity: int | None = Field(default=None, gt=0)
    from_ff_id: UUID | None = None
    to_ff_id: UUID | None = None
    transfer_id: UUID | None = None
    order_id: UUID | None = None
    shipment_id: UUID | None = None
    allow_cross_ff: bool = True

    @model_validator(mode="after")
    def require_fields_for_type(self):
        t = self.type
        if t == OperationKind.arrival:
            self._need(fulfillment_center_id=True, product_id=True, quantity=True)
        elif t == OperationKind.transfer_ship:
            self._need(from_ff_id=True, to_ff_id=True, product_id=True, quantity=True)
        elif t == OperationKind.transfer_receive:
            self._need(transfer_id=True)
        elif t == OperationKind.fbs_reserve:
            self._need(fulfillment_center_id=True, product_id=True, quantity=True)
        elif t in (OperationKind.fbs_ship, OperationKind.fbs_cancel):
            self._need(order_id=True)
        elif t == OperationKind.fbo_ship:
            self._need(fulfillment_center_id=True, product_id=True, quantity=True)
        elif t == OperationKind.fbo_accept:
            self._need(shipment_id=True)
        return self

    def _need(self, **flags: bool):
        missing = [name for name, required in flags.items() if required and getattr(self, name) is None]
        if missing:
            raise ValueError(f"Для type={self.type.value} обязательны: {', '.join(missing)}")


class ArrivalRequest(IdempotencyMixin):
    fulfillment_center_id: UUID
    product_id: UUID
    quantity: int = Field(gt=0)


class TransferShipRequest(IdempotencyMixin):
    from_ff_id: UUID
    to_ff_id: UUID
    product_id: UUID
    quantity: int = Field(gt=0)


class TransferReceiveRequest(IdempotencyMixin):
    transfer_id: UUID


class FbsReserveRequest(IdempotencyMixin):
    fulfillment_center_id: UUID
    product_id: UUID
    quantity: int = Field(gt=0)
    allow_cross_ff: bool = True


class FbsOrderActionRequest(IdempotencyMixin):
    order_id: UUID


class FboShipRequest(IdempotencyMixin):
    fulfillment_center_id: UUID
    product_id: UUID
    quantity: int = Field(gt=0)


class FboAcceptRequest(IdempotencyMixin):
    shipment_id: UUID