from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException

from checkstock_backend.api.schemas.product import ProductCreateModel, ProductModel
from checkstock_backend.db.models.product import Product

router = APIRouter()


@router.get(
    "",
    summary="Список товаров",
    status_code=200,
    response_model=List[ProductModel],
)
async def get_all():
    return await Product.all().order_by("sku")


@router.get(
    "/{product_id}",
    summary="Товар по ID",
    status_code=200,
    response_model=ProductModel,
)
async def get_by_id(product_id: UUID):
    product = await Product.get_or_none(id=product_id)
    if product is None:
        raise HTTPException(404, detail="Товар не найден")
    return product


@router.post(
    "",
    summary="Создать товар",
    status_code=201,
    response_model=ProductModel,
)
async def create(data: ProductCreateModel):
    product = await Product.create(**data.model_dump())
    return product


@router.put(
    "/{product_id}",
    summary="Обновить товар",
    status_code=200,
    response_model=ProductModel,
)
async def update(product_id: UUID, data: ProductCreateModel):
    product = await Product.get_or_none(id=product_id)
    if product is None:
        raise HTTPException(404, detail="Товар не найден")
    for attr, value in data.model_dump().items():
        setattr(product, attr, value)
    await product.save()
    return product


@router.delete(
    "/{product_id}",
    summary="Деактивировать товар",
    status_code=200,
    response_model=ProductModel,
)
async def delete(product_id: UUID):
    product = await Product.get_or_none(id=product_id)
    if product is None:
        raise HTTPException(404, detail="Товар не найден")
    product.is_active = False
    await product.save()
    return product