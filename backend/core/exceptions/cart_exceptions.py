from backend.core.exceptions.base import AppError

class ProductDeletedError(AppError):
    default_message = "Продукт был удален из корзины"
    error_code = "product_deleted"

class CartInsufficientStockError(AppError):
    error_code = "cart_insufficient_stock"
    status_code = 400

    def __init__(self, product_name, available_stock):
        self.product_name = product_name
        self.available_stock = available_stock
        super().__init__(f"Недостаточно товара '{product_name}' на складе. Доступно: {available_stock}")

class CartEmptyError(AppError):
    error_code = "cart_empty"
    status_code = 400
