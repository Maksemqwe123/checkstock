"""Учёт: приход, перемещения, FBS/FBO."""

from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from tortoise.transactions import atomic

from checkstock_backend.db.models.fbo_shipment import FboShipment
from checkstock_backend.db.models.fbs import FbsOrder, FbsOrderStatus, FbsReservationLine
from checkstock_backend.db.models.ful_fillment_center import FulfillmentCenter
from checkstock_backend.db.models.operation_log import OperationLog
from checkstock_backend.db.models.product import Product
from checkstock_backend.db.models.stock_balance import StockBalance
from checkstock_backend.db.models.stock_in_transit import StockInTransit, StockInTransitType
from checkstock_backend.db.models.transfer import Transfer, TransferStatus
from checkstock_backend.api.utils.exceptions import (
    AppError,
    IdempotencyConflictError,
    InsufficientStockError,
    NotFoundError,
)

from enum import Enum


class OperationType(str, Enum):
    ARRIVAL = "arrival"
    FF_RENAME = "ff_rename"
    FF_DELETE = "ff_delete"
    FF_CREATE = "ff_create"
    TRANSFER_SHIP = "transfer_ship"
    TRANSFER_RECEIVE = "transfer_receive"
    FBS_RESERVE = "fbs_reserve"
    FBS_SHIP = "fbs_ship"
    FBS_CANCEL = "fbs_cancel"
    FBO_SHIP = "fbo_ship"
    FBO_ACCEPT = "fbo_accept"
    CROSS_FF_ALLOCATE = "cross_ff_allocate"


def _ff_label(ff: FulfillmentCenter | None) -> str:
    if ff is None:
        return "?"
    if ff.is_active:
        return ff.name
    return f"{ff.name} (закрыт)"


async def _get_or_create_balance(ff_id: UUID, product_id: UUID) -> StockBalance:
    balance, _ = await StockBalance.get_or_create(
        fulfillment_center_id=ff_id,
        product_id=product_id,
        defaults={"physical_qty": 0, "reserved_fbs_qty": 0},
    )
    return balance


def _available(balance: StockBalance) -> int:
    return balance.physical_qty - balance.reserved_fbs_qty


async def _log(
    op_type: OperationType,
    description: str,
    idempotency_key: str | None = None,
    payload: dict[str, Any] | None = None,
) -> OperationLog:
    if idempotency_key:
        existing = await OperationLog.get_or_none(idempotency_key=idempotency_key)
        if existing:
            raise IdempotencyConflictError(
                f"Повтор: ключ {idempotency_key!r} — операция уже в журнале (#{existing.id})"
            )
    return await OperationLog.create(
        operation_type=op_type.value,
        idempotency_key=idempotency_key,
        description=description,
        payload_json=json.dumps(payload or {}, ensure_ascii=False),
    )


async def _active_ff(ff_id: UUID) -> FulfillmentCenter:
    ff = await FulfillmentCenter.get_or_none(id=ff_id)
    if ff is None:
        raise NotFoundError("Фулфилмент-центр не найден")
    if not ff.is_active:
        raise AppError("ФФ неактивен — новые операции недоступны", "ff_inactive")
    return ff


async def _product(product_id: UUID) -> Product:
    p = await Product.get_or_none(id=product_id)
    if p is None:
        raise NotFoundError("Товар не найден")
    return p


async def get_total_available(product_id: UUID, exclude_inactive: bool = True) -> int:
    total = 0
    for b in await StockBalance.filter(product_id=product_id):
        ff = await FulfillmentCenter.get_or_none(id=b.fulfillment_center_id)
        if exclude_inactive and ff and not ff.is_active:
            continue
        total += _available(b)
    return total


async def allocate_reservation_across_ffs(
    product_id: UUID,
    primary_ff_id: UUID,
    quantity: int,
) -> list[tuple[UUID, int]]:
    remaining = quantity
    lines: list[tuple[UUID, int]] = []
    primary = await _get_or_create_balance(primary_ff_id, product_id)
    take = min(_available(primary), remaining)
    if take > 0:
        lines.append((primary_ff_id, take))
        remaining -= take

    if remaining > 0:
        others = await StockBalance.filter(product_id=product_id).exclude(
            fulfillment_center_id=primary_ff_id
        )
        for bal in sorted(others, key=_available, reverse=True):
            ff = await FulfillmentCenter.get_or_none(id=bal.fulfillment_center_id)
            if ff is None or not ff.is_active:
                continue
            avail = _available(bal)
            if avail <= 0:
                continue
            take = min(avail, remaining)
            lines.append((bal.fulfillment_center_id, take))
            remaining -= take
            if remaining == 0:
                break

    if remaining > 0:
        total = await get_total_available(product_id)
        raise InsufficientStockError(
            f"Нехватка: нужно {quantity}, доступно по сети {total}"
        )
    return lines


class InventoryService:
    @atomic()
    async def arrival(
        self,
        ff_id: UUID,
        product_id: UUID,
        quantity: int,
        idempotency_key: str | None = None,
    ) -> StockBalance:
        if quantity <= 0:
            raise AppError("Количество должно быть > 0")
        ff = await _active_ff(ff_id)
        product = await _product(product_id)
        bal = await _get_or_create_balance(ff_id, product_id)
        bal.physical_qty += quantity
        await bal.save()
        await _log(
            OperationType.ARRIVAL,
            f"Приход {quantity} шт. {product.sku} на ФФ «{ff.name}»",
            idempotency_key,
            {
                "fulfillment_center_id": str(ff_id),
                "product_id": str(product_id),
                "quantity": quantity,
            },
        )
        return bal

    @atomic()
    async def ship_transfer(
        self,
        from_ff_id: UUID,
        to_ff_id: UUID,
        product_id: UUID,
        quantity: int,
        idempotency_key: str | None = None,
    ) -> Transfer:
        if from_ff_id == to_ff_id:
            raise AppError("ФФ отправления и назначения должны различаться")
        from_ff = await _active_ff(from_ff_id)
        to_ff = await _active_ff(to_ff_id)
        product = await _product(product_id)
        bal = await _get_or_create_balance(from_ff_id, product_id)
        if _available(bal) < quantity:
            raise InsufficientStockError(
                f"На «{from_ff.name}» доступно {_available(bal)}, нужно {quantity}"
            )
        bal.physical_qty -= quantity
        await bal.save()
        transfer = await Transfer.create(
            from_ff_id=from_ff_id,
            to_ff_id=to_ff_id,
            product_id=product_id,
            quantity=quantity,
            status=TransferStatus.IN_TRANSIT.value,
        )
        await StockInTransit.create(
            product_id=product_id,
            quantity=quantity,
            transit_type=StockInTransitType.BETWEEN_FF.value,
            fulfillment_center_from_id=from_ff_id,
            fulfillment_center_to_id=to_ff_id,
            transfer_id=transfer.id,
        )
        await _log(
            OperationType.TRANSFER_SHIP,
            f"Отгрузка {quantity} шт. {product.sku}: «{from_ff.name}» → «{to_ff.name}»",
            idempotency_key,
            {"transfer_id": str(transfer.id)},
        )
        return transfer

    @atomic()
    async def receive_transfer(
        self, transfer_id: UUID, idempotency_key: str | None = None
    ) -> Transfer:
        transfer = await Transfer.get_or_none(id=transfer_id)
        if transfer is None:
            raise NotFoundError("Перемещение не найдено")
        if transfer.status == TransferStatus.RECEIVED.value:
            if idempotency_key:
                existing = await OperationLog.get_or_none(idempotency_key=idempotency_key)
                if existing:
                    return transfer
            raise AppError("Перемещение уже принято", "already_received")
        if transfer.status != TransferStatus.IN_TRANSIT.value:
            raise AppError("Некорректный статус перемещения")

        to_ff = await FulfillmentCenter.get_or_none(id=transfer.to_ff_id)
        product = await _product(transfer.product_id)
        in_transit = await StockInTransit.get_or_none(transfer_id=transfer_id)
        if in_transit is None:
            raise AppError("Запись «в пути» не найдена")

        bal = await _get_or_create_balance(transfer.to_ff_id, transfer.product_id)
        bal.physical_qty += transfer.quantity
        await bal.save()
        transfer.status = TransferStatus.RECEIVED.value
        await transfer.save()
        await in_transit.delete()

        await _log(
            OperationType.TRANSFER_RECEIVE,
            f"Приём {transfer.quantity} шт. {product.sku} на {_ff_label(to_ff)}",
            idempotency_key,
            {"transfer_id": str(transfer_id)},
        )
        return transfer

    @atomic()
    async def reserve_fbs(
        self,
        fulfillment_center_id: UUID,
        product_id: UUID,
        quantity: int,
        allow_cross_ff: bool = True,
        idempotency_key: str | None = None,
    ) -> FbsOrder:
        await _active_ff(fulfillment_center_id)
        product = await _product(product_id)
        primary_bal = await _get_or_create_balance(fulfillment_center_id, product_id)

        if _available(primary_bal) >= quantity:
            lines = [(fulfillment_center_id, quantity)]
        elif allow_cross_ff:
            lines = await allocate_reservation_across_ffs(
                product_id, fulfillment_center_id, quantity
            )
        else:
            raise InsufficientStockError(
                f"На основном ФФ доступно {_available(primary_bal)}, нужно {quantity}"
            )

        order = await FbsOrder.create(
            fulfillment_center_id=fulfillment_center_id,
            product_id=product_id,
            quantity=quantity,
            status=FbsOrderStatus.RESERVED.value,
        )

        for ff_id, qty in lines:
            bal = await _get_or_create_balance(ff_id, product_id)
            bal.reserved_fbs_qty += qty
            await bal.save()
            await FbsReservationLine.create(
                order_id=order.id,
                fulfillment_center_id=ff_id,
                quantity=qty,
            )

        ff_names = []
        for ff_id, qty in lines:
            ff = await FulfillmentCenter.get_or_none(id=ff_id)
            ff_names.append(f"{_ff_label(ff)}: {qty}")

        op = OperationType.FBS_RESERVE
        if len(lines) > 1 or (lines and lines[0][0] != fulfillment_center_id):
            op = OperationType.CROSS_FF_ALLOCATE

        await _log(
            op,
            f"Резерв FBS {quantity} шт. {product.sku} ({', '.join(ff_names)})",
            idempotency_key,
            {"order_id": str(order.id), "lines": [(str(a), b) for a, b in lines]},
        )
        await order.fetch_related("reservation_lines")
        return order

    @atomic()
    async def ship_fbs(
        self, order_id: UUID, idempotency_key: str | None = None
    ) -> FbsOrder:
        order = await FbsOrder.filter(id=order_id).prefetch_related("reservation_lines").first()
        if order is None:
            raise NotFoundError("Заказ FBS не найден")
        if order.status == FbsOrderStatus.SHIPPED.value:
            if idempotency_key and await OperationLog.get_or_none(idempotency_key=idempotency_key):
                return order
            raise AppError("Заказ уже отправлен", "already_shipped")
        if order.status != FbsOrderStatus.RESERVED.value:
            raise AppError("Заказ нельзя отправить в текущем статусе")

        product = await _product(order.product_id)
        for line in await order.reservation_lines.all():
            bal = await _get_or_create_balance(line.fulfillment_center_id, order.product_id)
            if bal.physical_qty < line.quantity or bal.reserved_fbs_qty < line.quantity:
                raise AppError("Расхождение резерва и физического остатка")
            bal.physical_qty -= line.quantity
            bal.reserved_fbs_qty -= line.quantity
            await bal.save()

        await StockInTransit.create(
            product_id=order.product_id,
            quantity=order.quantity,
            transit_type=StockInTransitType.TO_FBS_CUSTOMER.value,
            fulfillment_center_from_id=order.fulfillment_center_id,
            fbs_order_id=order.id,
        )
        order.status = FbsOrderStatus.SHIPPED.value
        await order.save()
        await _log(
            OperationType.FBS_SHIP,
            f"Отправка FBS {order.quantity} шт. {product.sku} (заказ #{order.id})",
            idempotency_key,
            {"order_id": str(order_id)},
        )
        return order

    @atomic()
    async def cancel_fbs(
        self, order_id: UUID, idempotency_key: str | None = None
    ) -> FbsOrder:
        order = await FbsOrder.filter(id=order_id).prefetch_related("reservation_lines").first()
        if order is None:
            raise NotFoundError("Заказ FBS не найден")
        if order.status == FbsOrderStatus.CANCELLED.value:
            return order
        if order.status != FbsOrderStatus.RESERVED.value:
            raise AppError("Отмена возможна только для зарезервированного заказа")

        product = await _product(order.product_id)
        for line in await order.reservation_lines.all():
            bal = await _get_or_create_balance(line.fulfillment_center_id, order.product_id)
            bal.reserved_fbs_qty -= line.quantity
            await bal.save()

        order.status = FbsOrderStatus.CANCELLED.value
        await order.save()
        await _log(
            OperationType.FBS_CANCEL,
            f"Отмена FBS заказа #{order.id}, {product.sku}",
            idempotency_key,
            {"order_id": str(order_id)},
        )
        return order

    @atomic()
    async def ship_fbo(
        self,
        fulfillment_center_id: UUID,
        product_id: UUID,
        quantity: int,
        idempotency_key: str | None = None,
    ) -> FboShipment:
        from_ff = await _active_ff(fulfillment_center_id)
        product = await _product(product_id)
        bal = await _get_or_create_balance(fulfillment_center_id, product_id)
        if _available(bal) < quantity:
            raise InsufficientStockError()
        bal.physical_qty -= quantity
        await bal.save()
        shipment = await FboShipment.create(
            fulfillment_center_id=fulfillment_center_id,
            product_id=product_id,
            quantity=quantity,
        )
        await StockInTransit.create(
            product_id=product_id,
            quantity=quantity,
            transit_type=StockInTransitType.TO_FBO.value,
            fulfillment_center_from_id=fulfillment_center_id,
            fbo_shipment_id=shipment.id,
        )
        await _log(
            OperationType.FBO_SHIP,
            f"Отгрузка FBO {quantity} шт. {product.sku} с «{from_ff.name}»",
            idempotency_key,
            {"shipment_id": str(shipment.id)},
        )
        return shipment

    @atomic()
    async def accept_fbo(
        self, shipment_id: UUID, idempotency_key: str | None = None
    ) -> FboShipment:
        shipment = await FboShipment.get_or_none(id=shipment_id)
        if shipment is None:
            raise NotFoundError("Поставка FBO не найдена")
        if shipment.accepted:
            if idempotency_key and await OperationLog.get_or_none(idempotency_key=idempotency_key):
                return shipment
            raise AppError("FBO уже принят маркетплейсом", "already_accepted")

        product = await _product(shipment.product_id)
        in_transit = await StockInTransit.get_or_none(fbo_shipment_id=shipment_id)
        if in_transit:
            await in_transit.delete()
        shipment.accepted = True
        await shipment.save()
        await _log(
            OperationType.FBO_ACCEPT,
            f"Маркетплейс принял FBO {shipment.quantity} шт. {product.sku}",
            idempotency_key,
            {"shipment_id": str(shipment_id)},
        )
        return shipment