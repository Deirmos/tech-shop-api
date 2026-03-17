class CategoryError(Exception):
    default_message = "Произошла ошибка с категорией"
    error_code = "category_error"
    status_code = 400

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)

class CategoryNotFoundError(CategoryError):
    error_code = "category_not_found"
    status_code = 404

    def __init__(self, category_id):
        self.category_id = category_id
        super().__init__(f"Категория с id {category_id} не найдена")

class CategoryNotEmptyError(CategoryError):
    default_message = "Нельзя удалить категорию, которая содержит товары"
    error_code = "category_not_empty"
    status_code = 400

class CategoryNotDeletedError(CategoryError):
    default_message = "Нельзя восстановить не удаленную категорию"
    error_code = "category_not_deleted"
    status_code = 400