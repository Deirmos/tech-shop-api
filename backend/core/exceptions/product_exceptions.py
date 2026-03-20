from backend.core.exceptions.base import AppError

class ProductNotFoundError(AppError):
    error_code = "product_not_found"
    status_code = 404

    def __init__(self, product_id):
        self.product_id = product_id
        super().__init__(f"Товар с id({product_id}) не найден")

class ProductAlreadyExistsError(AppError):
    error_code = "product_already_exists"
    status_code = 400

    def __init__(self, product_name):
        self.product_name = product_name
        super().__init__(f"Товар с названием '{product_name}' уже существует")

class ProductNotDeletedError(AppError):
    default_message = "Нельзя восстановить не удаленный товар"
    error_code = "product_not_deleted"
    status_code = 400

class ProductInsufficientStockError(AppError):
    error_code = "product_insufficient_stock"
    status_code = 400

    def __init__(self, product_name):
        self.product_name = product_name
        super().__init__(f"Недостаточно товара '{product_name}' на складе")

class ProductMissingImageNameError(AppError):
    error_code = "product_missing_image_name"
    status_code = 400
    default_message = "Файл без имени недопустим"

class ProductInvalidImageExtensionError(AppError):
    error_code = "product_invalid_image_extension"
    status_code = 400
    
    def __init__(self, allowed_extensions):
        self.allowed_extensions = allowed_extensions
        super().__init__(f"Недопустимое расширение файла. Разрешены: {allowed_extensions}")

class ProductTooLargeImageError(AppError):
    error_code = "product_too_large_image"
    status_code = 400
    default_message = "Файл слишком большой. Максимальный размер: 5 МБ"

class ProductInvalidImageFormatError(AppError):
    error_code = "product_invalid_image_format"
    status_code = 400
    default_message = "Неверный внутренний формат изображения"

class ProductInvalidImageError(AppError):
    error_code = "product_invalid_image"
    status_code = 400
    default_message = "Файл поврежден или не является валидным изображением"
