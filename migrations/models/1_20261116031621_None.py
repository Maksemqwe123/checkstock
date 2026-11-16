from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "fulfillment_centers" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(120) NOT NULL,
    "code" VARCHAR(10) NOT NULL,
    "city" VARCHAR(100) NOT NULL,
    "address" TEXT NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "fulfillment_centers"."id" IS 'Идентификатор центра отгрузки';
COMMENT ON COLUMN "fulfillment_centers"."name" IS 'Название центра отгрузки';
COMMENT ON COLUMN "fulfillment_centers"."code" IS 'Код центра отгрузки';
COMMENT ON COLUMN "fulfillment_centers"."city" IS 'Город центра отгрузки';
COMMENT ON COLUMN "fulfillment_centers"."address" IS 'Адрес центра отгрузки';
COMMENT ON COLUMN "fulfillment_centers"."is_active" IS 'Активен ли центр отгрузки';
COMMENT ON COLUMN "fulfillment_centers"."created" IS 'Дата создания центра отгрузки';
COMMENT ON COLUMN "fulfillment_centers"."updated" IS 'Дата последнего обновления центра отгрузки';
CREATE TABLE IF NOT EXISTS "products" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "sku" VARCHAR(64) NOT NULL UNIQUE,
    "name" VARCHAR(200) NOT NULL,
    "description" TEXT,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "products"."id" IS 'Идентификатор продукта';
COMMENT ON COLUMN "products"."sku" IS 'SKU продукта';
COMMENT ON COLUMN "products"."name" IS 'Название продукта';
COMMENT ON COLUMN "products"."description" IS 'Описание продукта';
COMMENT ON COLUMN "products"."is_active" IS 'Активен ли продукт';
COMMENT ON COLUMN "products"."created" IS 'Дата создания продукта';
COMMENT ON COLUMN "products"."updated" IS 'Дата последнего обновления продукта';
CREATE TABLE IF NOT EXISTS "stock_balances" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "physical_qty" INT NOT NULL  DEFAULT 0,
    "reserved_fbs_qty" INT NOT NULL  DEFAULT 0,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "fulfillment_center_id" UUID NOT NULL REFERENCES "fulfillment_centers" ("id") ON DELETE CASCADE,
    "product_id" UUID NOT NULL REFERENCES "products" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_stock_balan_fulfill_f28e99" UNIQUE ("fulfillment_center_id", "product_id")
);
COMMENT ON COLUMN "stock_balances"."id" IS 'Идентификатор баланса остатков';
COMMENT ON COLUMN "stock_balances"."physical_qty" IS 'Физический остаток';
COMMENT ON COLUMN "stock_balances"."reserved_fbs_qty" IS 'Зарезервированный остаток для FBS';
COMMENT ON COLUMN "stock_balances"."created" IS 'Дата создания баланса остатков';
COMMENT ON COLUMN "stock_balances"."updated" IS 'Дата последнего обновления баланса остатков';
CREATE TABLE IF NOT EXISTS "transfers" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "quantity" INT NOT NULL  DEFAULT 0,
    "status" VARCHAR(32) NOT NULL  DEFAULT 'in_transit',
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "from_ff_id" UUID NOT NULL REFERENCES "fulfillment_centers" ("id") ON DELETE CASCADE,
    "product_id" UUID NOT NULL REFERENCES "products" ("id") ON DELETE CASCADE,
    "to_ff_id" UUID NOT NULL REFERENCES "fulfillment_centers" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "transfers"."id" IS 'Идентификатор перевода';
COMMENT ON COLUMN "transfers"."quantity" IS 'Количество перевода';
COMMENT ON COLUMN "transfers"."status" IS 'Статус перевода';
COMMENT ON COLUMN "transfers"."created" IS 'Дата создания перевода';
COMMENT ON COLUMN "transfers"."updated" IS 'Дата последнего обновления перевода';
CREATE TABLE IF NOT EXISTS "fbs_orders" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "quantity" INT NOT NULL  DEFAULT 0,
    "status" VARCHAR(32) NOT NULL  DEFAULT 'reserved',
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "fulfillment_center_id" UUID NOT NULL REFERENCES "fulfillment_centers" ("id") ON DELETE CASCADE,
    "product_id" UUID NOT NULL REFERENCES "products" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "fbs_orders"."id" IS 'Идентификатор заказа FBS';
COMMENT ON COLUMN "fbs_orders"."quantity" IS 'Количество заказа FBS';
COMMENT ON COLUMN "fbs_orders"."created" IS 'Дата создания заказа FBS';
COMMENT ON COLUMN "fbs_orders"."updated" IS 'Дата последнего обновления заказа FBS';
CREATE TABLE IF NOT EXISTS "fbs_reservation_lines" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "quantity" INT NOT NULL  DEFAULT 0,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "fulfillment_center_id" UUID NOT NULL REFERENCES "fulfillment_centers" ("id") ON DELETE CASCADE,
    "order_id" UUID NOT NULL REFERENCES "fbs_orders" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "fbs_reservation_lines"."id" IS 'Идентификатор линии резервации FBS';
COMMENT ON COLUMN "fbs_reservation_lines"."quantity" IS 'Количество линии резервации FBS';
COMMENT ON COLUMN "fbs_reservation_lines"."created" IS 'Дата создания линии резервации FBS';
COMMENT ON COLUMN "fbs_reservation_lines"."updated" IS 'Дата последнего обновления линии резервации FBS';
CREATE TABLE IF NOT EXISTS "fbo_shipments" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "quantity" INT NOT NULL  DEFAULT 0,
    "accepted" BOOL NOT NULL  DEFAULT False,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "fulfillment_center_id" UUID NOT NULL REFERENCES "fulfillment_centers" ("id") ON DELETE CASCADE,
    "product_id" UUID NOT NULL REFERENCES "products" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "fbo_shipments"."id" IS 'Идентификатор отгрузки FBO';
COMMENT ON COLUMN "fbo_shipments"."quantity" IS 'Количество отгрузки FBO';
COMMENT ON COLUMN "fbo_shipments"."accepted" IS 'Принят ли отгрузка FBO';
COMMENT ON COLUMN "fbo_shipments"."created" IS 'Дата создания отгрузки FBO';
COMMENT ON COLUMN "fbo_shipments"."updated" IS 'Дата последнего обновления отгрузки FBO';
CREATE TABLE IF NOT EXISTS "stock_in_transit" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "quantity" INT NOT NULL  DEFAULT 0,
    "transit_type" VARCHAR(32) NOT NULL,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "fbo_shipment_id" UUID REFERENCES "fbo_shipments" ("id") ON DELETE CASCADE,
    "fbs_order_id" UUID REFERENCES "fbs_orders" ("id") ON DELETE CASCADE,
    "fulfillment_center_from_id" UUID REFERENCES "fulfillment_centers" ("id") ON DELETE CASCADE,
    "fulfillment_center_to_id" UUID REFERENCES "fulfillment_centers" ("id") ON DELETE CASCADE,
    "product_id" UUID NOT NULL REFERENCES "products" ("id") ON DELETE CASCADE,
    "transfer_id" UUID REFERENCES "transfers" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "stock_in_transit"."id" IS 'Идентификатор строки в пути перемещения';
COMMENT ON COLUMN "stock_in_transit"."quantity" IS 'Количество в пути перемещения';
COMMENT ON COLUMN "stock_in_transit"."transit_type" IS 'Тип пути перемещения';
COMMENT ON COLUMN "stock_in_transit"."created" IS 'Дата создания строки в пути перемещения';
COMMENT ON COLUMN "stock_in_transit"."updated" IS 'Дата последнего обновления строки в пути перемещения';
CREATE TABLE IF NOT EXISTS "operation_logs" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "operation_type" VARCHAR(64) NOT NULL,
    "idempotency_key" VARCHAR(128)  UNIQUE,
    "description" TEXT NOT NULL,
    "payload_json" TEXT,
    "created" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "operation_logs"."id" IS 'Идентификатор операции';
COMMENT ON COLUMN "operation_logs"."operation_type" IS 'Тип операции';
COMMENT ON COLUMN "operation_logs"."description" IS 'Описание операции';
COMMENT ON COLUMN "operation_logs"."payload_json" IS 'JSON payload операции';
COMMENT ON COLUMN "operation_logs"."created" IS 'Дата создания операции';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
