class ProductError(Exception):
    default_message = "Произошла ошибка с товаром"
    error_code = "product_error"
    status_code = 400

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)

class ProductNotFoundError(ProductError):
    error_code = "product_not_found"
    status_code = 404

    def __init__(self, product_id):
        self.product_id = product_id
        super().__init__(f"Товар с id({product_id}) не найден")

class ProductAlreadyExistsError(ProductError):
    error_code = "product_already_exists"
    status_code = 400

    def __init__(self, product_name):
        self.product_name = product_name
        super().__init__(f"Товар с названием '{product_name}' уже существует")

class ProductNotDeletedError(ProductError):
    default_message = "Нельзя восстановить не удаленный товар"
    error_code = "product_not_deleted"
    status_code = 400

class ProductInsufficientStockError(ProductError):
    error_code = "product_insufficient_stock"
    status_code = 400

    def __init__(self, product_name):
        self.product_name = product_name
        super().__init__(f"Недостаточно товара '{product_name}' на складе")