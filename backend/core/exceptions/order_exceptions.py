from backend.core.exceptions.base import AppError

class OrderNotFoundError(AppError):
    error_code = "order_not_found"
    status_code = 404

    def __init__(self, order_id):
        self.order_id = order_id
        super().__init__(f"Заказ с id({order_id}) не найден")

class OrderAdminRequiredError(AppError):
    default_message = "У вас недостоточно прав"
    error_code = "order_admin_required"
    status_code = 403

class OrderInvalidStatusTransitionError(AppError):
    error_code = "order_invalid_status_transition"
    status_code = 400



