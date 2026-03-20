from backend.core.exceptions.base import AppError

class CategoryNotFoundError(AppError):
    error_code = "category_not_found"
    status_code = 404

    def __init__(self, category_id):
        self.category_id = category_id
        super().__init__(f"Категория с id {category_id} не найдена")

class CategoryNotEmptyError(AppError):
    default_message = "Нельзя удалить категорию, которая содержит товары"
    error_code = "category_not_empty"
    status_code = 400

class CategoryNotDeletedError(AppError):
    default_message = "Нельзя восстановить не удаленную категорию"
    error_code = "category_not_deleted"
    status_code = 400