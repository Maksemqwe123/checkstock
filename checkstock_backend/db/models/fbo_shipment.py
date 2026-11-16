from tortoise import fields
from tortoise.models import Model


class FboShipment(Model):
    id = fields.UUIDField(pk=True, description="Идентификатор отгрузки FBO")
    fulfillment_center = fields.ForeignKeyField(
        "models.FulfillmentCenter", related_name="fbo_shipments", on_delete=fields.CASCADE
    )
    product = fields.ForeignKeyField("models.Product", related_name="fbo_shipments", on_delete=fields.CASCADE)
    quantity = fields.IntField(null=False, default=0, description="Количество отгрузки FBO")
    accepted = fields.BooleanField(default=False, description="Принят ли отгрузка FBO")
    created = fields.DatetimeField(auto_now_add=True, description="Дата создания отгрузки FBO")
    updated = fields.DatetimeField(auto_now=True, description="Дата последнего обновления отгрузки FBO")

    class Meta:
        table = "fbo_shipments"
