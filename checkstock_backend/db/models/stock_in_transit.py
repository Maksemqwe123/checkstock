from tortoise import fields
from tortoise.models import Model
from enum import Enum


class StockInTransitType(str, Enum):
    BETWEEN_FF = "between_ff"
    TO_FBO = "to_fbo"
    TO_FBS_CUSTOMER = "to_fbs_customer"


class StockInTransit(Model):
    id = fields.UUIDField(pk=True, description="Идентификатор строки в пути перемещения")
    product = fields.ForeignKeyField("models.Product", related_name="in_transit_rows", on_delete=fields.CASCADE)
    quantity = fields.IntField(null=False, default=0, description="Количество в пути перемещения")
    transit_type = fields.CharField(max_length=32, description="Тип пути перемещения")
    fulfillment_center_from = fields.ForeignKeyField("models.FulfillmentCenter", related_name="in_transit_from", null=True, on_delete=fields.CASCADE)
    fulfillment_center_to = fields.ForeignKeyField("models.FulfillmentCenter", related_name="in_transit_to", null=True, on_delete=fields.CASCADE)
    transfer = fields.ForeignKeyField("models.Transfer", related_name="in_transit_row", null=True, on_delete=fields.CASCADE)
    fbs_order = fields.ForeignKeyField("models.FbsOrder", related_name="in_transit_row", null=True, on_delete=fields.CASCADE)
    fbo_shipment = fields.ForeignKeyField("models.FboShipment", related_name="in_transit_row", null=True, on_delete=fields.CASCADE)
    created = fields.DatetimeField(auto_now_add=True, description="Дата создания строки в пути перемещения")
    updated = fields.DatetimeField(auto_now=True, description="Дата последнего обновления строки в пути перемещения")

    class Meta:
        table = "stock_in_transit"