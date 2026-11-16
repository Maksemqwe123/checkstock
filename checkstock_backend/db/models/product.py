from tortoise import fields
from tortoise.models import Model


class Product(Model):
    id = fields.UUIDField(pk=True, description="Идентификатор продукта")
    sku = fields.CharField(null=False, max_length=64, unique=True, description="SKU продукта")
    name = fields.CharField(null=False, max_length=200, description="Название продукта")
    description = fields.TextField(null=True, description="Описание продукта")
    is_active = fields.BooleanField(default=True, null=False, description="Активен ли продукт")
    created = fields.DatetimeField(auto_now_add=True, description="Дата создания продукта")
    updated = fields.DatetimeField(auto_now=True, description="Дата последнего обновления продукта")

    class Meta:
        table = "products"
