from tortoise import fields
from tortoise.models import Model
from enum import Enum


class FbsOrderStatus(str, Enum):
    RESERVED = "reserved"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class FbsOrder(Model):
    id = fields.UUIDField(pk=True, description="Идентификатор заказа FBS")
    fulfillment_center = fields.ForeignKeyField(
        "models.FulfillmentCenter", related_name="fbs_orders_primary", on_delete=fields.CASCADE
    )
    product = fields.ForeignKeyField("models.Product", related_name="fbs_orders", on_delete=fields.CASCADE)
    quantity = fields.IntField(null=False, default=0, description="Количество заказа FBS")
    status = fields.CharField(max_length=32, default=FbsOrderStatus.RESERVED.value)
    created = fields.DatetimeField(auto_now_add=True, description="Дата создания заказа FBS")
    updated = fields.DatetimeField(auto_now=True, description="Дата последнего обновления заказа FBS")

    reservation_lines: fields.ReverseRelation["FbsReservationLine"]

    class Meta:
        table = "fbs_orders"


class FbsReservationLine(Model):
    id = fields.UUIDField(pk=True, description="Идентификатор линии резервации FBS")
    order = fields.ForeignKeyField(
        "models.FbsOrder", related_name="reservation_lines", on_delete=fields.CASCADE
    )
    fulfillment_center = fields.ForeignKeyField(
        "models.FulfillmentCenter", related_name="fbs_reservation_lines", on_delete=fields.CASCADE
    )
    quantity = fields.IntField(null=False, default=0, description="Количество линии резервации FBS")
    created = fields.DatetimeField(auto_now_add=True, description="Дата создания линии резервации FBS")
    updated = fields.DatetimeField(auto_now=True, description="Дата последнего обновления линии резервации FBS")

    class Meta:
        table = "fbs_reservation_lines"
