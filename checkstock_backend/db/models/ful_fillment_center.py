from tortoise import fields
from tortoise.models import Model


class FulfillmentCenter(Model):
    id = fields.UUIDField(pk=True, description="Идентификатор центра отгрузки")
    name = fields.CharField(null=False, max_length=120, description="Название центра отгрузки")
    code = fields.CharField(null=False, max_length=10, description="Код центра отгрузки")
    city = fields.CharField(null=False, max_length=100, description="Город центра отгрузки")
    address = fields.TextField(null=False, description="Адрес центра отгрузки")
    is_active = fields.BooleanField(default=True, null=False, description="Активен ли центр отгрузки")
    created = fields.DatetimeField(auto_now_add=True, description="Дата создания центра отгрузки")
    updated = fields.DatetimeField(auto_now=True, description="Дата последнего обновления центра отгрузки")

    class Meta:
        table = "fulfillment_centers"
