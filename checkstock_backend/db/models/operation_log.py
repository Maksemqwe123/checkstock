from tortoise import fields
from tortoise.models import Model


class OperationLog(Model):
    id = fields.UUIDField(pk=True, description="Идентификатор операции")
    operation_type = fields.CharField(max_length=64, description="Тип операции")
    idempotency_key = fields.CharField(max_length=128, null=True, unique=True)
    description = fields.TextField(description="Описание операции")
    payload_json = fields.TextField(null=True, description="JSON payload операции")
    created = fields.DatetimeField(auto_now_add=True, description="Дата создания операции")

    class Meta:
        table = "operation_logs"
