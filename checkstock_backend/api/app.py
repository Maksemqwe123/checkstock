import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist
from starlette.requests import Request
from starlette.responses import JSONResponse

from checkstock_backend.api.routes.fbo_shipments import router as fbo_router
from checkstock_backend.api.routes.fbs_orders import router as fbs_router
from checkstock_backend.api.routes.ful_fillment_centers import router as fulfillment_centers_router
from checkstock_backend.api.routes.inventory import router as inventory_router
from checkstock_backend.api.routes.operation_logs import router as logs_router
from checkstock_backend.api.routes.operations import router as operations_router
from checkstock_backend.api.routes.products import router as products_router
from checkstock_backend.api.routes.stock_balances import router as balances_router
from checkstock_backend.api.routes.stock_in_transit import router as transit_router
from checkstock_backend.api.routes.transfers import router as transfers_router
from checkstock_backend.db.config import TORTOISE_ORM

app = FastAPI(
    title="Checkstock API",
    description="API для работы с Checkstock",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DoesNotExist)
async def does_not_exist_exception_handler(request: Request, exc: DoesNotExist):
    return JSONResponse(
        status_code=404,
        content={"detail": "Данные не найдены", "code": "not_found"},
    )


@app.on_event("startup")
async def startup():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    app.include_router(
        fulfillment_centers_router,
        prefix="/fulfillment-centers",
        tags=["Склады"],
    )
    app.include_router(
        products_router,
        prefix="/products",
        tags=["Товары"],
    )
    app.include_router(
        balances_router,
        prefix="/stock-balances",
        tags=["Остатки"],
    )
    app.include_router(
        transfers_router,
        prefix="/transfers",
        tags=["Перемещения"],
    )
    app.include_router(
        fbs_router,
        prefix="/fbs-orders",
        tags=["FBS"],
    )
    app.include_router(
        fbo_router,
        prefix="/fbo-shipments",
        tags=["FBO"],
    )
    app.include_router(
        transit_router,
        prefix="/stock-in-transit",
        tags=["В пути"],
    )
    app.include_router(
        logs_router,
        prefix="/operation-logs",
        tags=["Журнал"],
    )
    app.include_router(
        inventory_router,
        prefix="/inventory",
        tags=["Сводки"],
    )
    app.include_router(
        operations_router,
        prefix="/operations",
        tags=["Операции учёта"],
    )


@app.on_event("shutdown")
async def shutdown():
    await Tortoise.close_connections()


def run():
    run_dict = {
        "app": "checkstock_backend.api.app:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,
    }

    uvicorn.run(**run_dict)


if __name__ == "__main__":
    run()