class OrderError(Exception):
    default_message = "Произошла ошибка с заказом"
    error_code = "order_error"
    status_code = 400

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)

class OrderNotFoundError(OrderError):
    error_code = "order_not_found"
    status_code = 404

    def __init__(self, order_id):
        self.order_id = order_id
        super().__init__(f"Заказ с id({order_id}) не найден")

class OrderAdminRequiredError(OrderError):
    default_message = "У вас недостоточно прав"
    error_code = "order_admin_required"
    status_code = 403

class OrderInvalidStatusTransitionError(OrderError):
    error_code = "order_invalid_status_transition"
    status_code = 400



