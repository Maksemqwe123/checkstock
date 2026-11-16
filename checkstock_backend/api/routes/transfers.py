from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException

from checkstock_backend.api.schemas.responses import TransferOut
from checkstock_backend.db.models.transfer import Transfer

router = APIRouter()


@router.get(
    "",
    summary="Список перемещений",
    status_code=200,
    response_model=List[TransferOut],
)
async def list_transfers():
    return await Transfer.all().order_by("-created")


@router.get(
    "/{transfer_id}",
    summary="Перемещение по ID",
    status_code=200,
    response_model=TransferOut,
)
async def get_transfer(transfer_id: UUID):
    transfer = await Transfer.get_or_none(id=transfer_id)
    if transfer is None:
        raise HTTPException(404, detail="Перемещение не найдено")
    return transfer