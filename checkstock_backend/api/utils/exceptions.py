class AppError(Exception):
    def __init__(self, message: str, code: str = "error"):
        self.message = message
        self.code = code
        super().__init__(message)


class InsufficientStockError(AppError):
    def __init__(self, message: str = "Недостаточно товара"):
        super().__init__(message, "insufficient_stock")


class IdempotencyConflictError(AppError):
    def __init__(self, message: str = "Операция с таким ключом уже выполнена"):
        super().__init__(message, "idempotency_replay")


class NotFoundError(AppError):
    def __init__(self, message: str = "Не найдено"):
        super().__init__(message, "not_found")