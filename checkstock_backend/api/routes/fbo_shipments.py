from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException

from checkstock_backend.api.schemas.responses import FboShipmentOut
from checkstock_backend.db.models.fbo_shipment import FboShipment

router = APIRouter()


@router.get(
    "",
    summary="Отгрузки FBO",
    status_code=200,
    response_model=List[FboShipmentOut],
)
async def list_shipments():
    return await FboShipment.all().order_by("-created")


@router.get(
    "/{shipment_id}",
    summary="Отгрузка FBO по ID",
    status_code=200,
    response_model=FboShipmentOut,
)
async def get_shipment(shipment_id: UUID):
    shipment = await FboShipment.get_or_none(id=shipment_id)
    if shipment is None:
        raise HTTPException(404, detail="Отгрузка FBO не найдена")
    return shipment