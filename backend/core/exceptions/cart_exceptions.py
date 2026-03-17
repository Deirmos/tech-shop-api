class CartError(Exception):
    default_message = "Произошла ошибка с корзиной"
    error_code = "cart_error"
    status_code = 400

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)

class ProductNotFoundError(CartError):
    error_code = "product_not_found"
    status_code = 404

    def __init__(self, product_id):
        self.product_id = product_id
        super().__init__(f"Товар с id {product_id} не найден")

class ProductDeletedError(CartError):
    default_message = "Продукт был удален из корзины"
    error_code = "product_deleted"

class InsufficientStockError(CartError):
    default_message = "Недостаточно товара на складе"
    error_code = "insufficient_stock"

class CartEmptyError(CartError):
    error_code = "cart_empty"
    status_code = 400
