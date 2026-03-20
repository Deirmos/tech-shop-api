class AppError(Exception):
    default_message = "Произошла ошибка"
    error_code = "app_error"
    status_code = 400

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)