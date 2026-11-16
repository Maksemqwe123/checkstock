from checkstock_backend.api.settings import ENVS

TORTOISE_ORM = {
    "connections": {
        "default": (
            f"postgres://{ENVS.pg_user}:{ENVS.pg_password}"
            f"@{ENVS.pg_host}:{ENVS.pg_port}/{ENVS.pg_db}"
        ),
    },
    "apps": {
        "models": {
            "models": [
                "checkstock_backend.db.models.ful_fillment_center",
                "checkstock_backend.db.models.product",
                "checkstock_backend.db.models.stock_balance",
                "checkstock_backend.db.models.transfer",
                "checkstock_backend.db.models.fbs",
                "checkstock_backend.db.models.fbo_shipment",
                "checkstock_backend.db.models.stock_in_transit",
                "checkstock_backend.db.models.operation_log",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}