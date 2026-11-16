from tortoise import fields
from tortoise.models import Model

from enum import Enum


class TransferStatus(str, Enum):
    IN_TRANSIT = "in_transit"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class Transfer(Model):
    id = fields.UUIDField(pk=True, description="Идентификатор перевода")
    from_ff = fields.ForeignKeyField(
        "models.FulfillmentCenter", related_name="transfers_out", on_delete=fields.CASCADE
    )
    to_ff = fields.ForeignKeyField(
        "models.FulfillmentCenter", related_name="transfers_in", on_delete=fields.CASCADE
    )
    product = fields.ForeignKeyField("models.Product", related_name="transfers", on_delete=fields.CASCADE)
    quantity = fields.IntField(null=False, default=0, description="Количество перевода")
    status = fields.CharField(max_length=32, default=TransferStatus.IN_TRANSIT.value, description="Статус перевода")
    created = fields.DatetimeField(auto_now_add=True, description="Дата создания перевода")
    updated = fields.DatetimeField(auto_now=True, description="Дата последнего обновления перевода")

    class Meta:
        table = "transfers"
