from fastapi import APIRouter
from uuid import UUID

from checkstock_backend.api.schemas.ful_fillment_center import FulfillmentCenterModel, FulfillmentCenterCreateModel
from checkstock_backend.db.models.ful_fillment_center import FulfillmentCenter

from typing import List

router = APIRouter()


@router.get(
    '',
    summary='Получение всех складов',
    status_code=200,
    response_model=List[FulfillmentCenterModel]
)
async def getAll():
    fulfillment_centers = await FulfillmentCenter.all()
    return fulfillment_centers


@router.get(
    '/{id}',
    summary='Получение склада по ID',
    status_code=200,
    response_model=FulfillmentCenterModel
)
async def getById(id: UUID):
    fulfillment_center = await FulfillmentCenter.get(id=id)
    return fulfillment_center


@router.post(
    '',
    summary='Создание склада',
    status_code=200,
    response_model=FulfillmentCenterModel
)
async def post(data: FulfillmentCenterCreateModel):
    fulfillment_center = FulfillmentCenter(**data.model_dump())
    await fulfillment_center.save()

    return fulfillment_center


@router.put(
    '/{id}',
    summary='Обновление склада',
    status_code=200,
    response_model=FulfillmentCenterModel
)
async def put(id: UUID, data: FulfillmentCenterCreateModel):
    fulfillment_center = await FulfillmentCenter.get(id=id)


    for (attr, value) in data.model_dump().items():
        if value is not None:
            setattr(fulfillment_center, attr, value)

    await fulfillment_center.save()
    return fulfillment_center


@router.delete(
    '/{id}',
    summary='Удаление склада',
    status_code=200,
    response_model=FulfillmentCenterModel
)
async def delete(id: UUID):
    fulfillment_center = await FulfillmentCenter.get(id=id)

    fulfillment_center.is_active = False

    await fulfillment_center.save()

    return fulfillment_center
