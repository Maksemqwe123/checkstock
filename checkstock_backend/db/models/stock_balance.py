from tortoise import fields
from tortoise.models import Model


class StockBalance(Model):
    id = fields.UUIDField(pk=True, description="Идентификатор баланса остатков")
    fulfillment_center = fields.ForeignKeyField(
        "models.FulfillmentCenter", related_name="stock_balances", on_delete=fields.CASCADE
    )
    product = fields.ForeignKeyField("models.Product", related_name="stock_balances", on_delete=fields.CASCADE)
    physical_qty = fields.IntField(default=0, description="Физический остаток")
    reserved_fbs_qty = fields.IntField(default=0, description="Зарезервированный остаток для FBS")
    created = fields.DatetimeField(auto_now_add=True, description="Дата создания баланса остатков")
    updated = fields.DatetimeField(auto_now=True, description="Дата последнего обновления баланса остатков")

    class Meta:
        table = "stock_balances"
        unique_together = (("fulfillment_center", "product"),)
