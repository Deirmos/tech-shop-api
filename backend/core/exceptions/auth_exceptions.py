class UserError(Exception):
    default_message = "Произошла ошибка"
    error_code = "app_error"
    status_code = 400

    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)

class AuthenticationError(UserError):
    default_message = "Невалидный токен"
    error_code = "authentication"
    status_code = 401
    

class AuthorizationError(UserError):
    default_message = "Недостаточно прав для доступа к ресурсу"
    error_code = "authorization"
    status_code = 403

class InvalidCredentialsError(UserError):
    default_message = "Неверные учетные данные"
    error_code = "invalid_credentials"
    status_code = 401

class UserAlreadyExistsError(UserError):
    default_message = "Пользователь с таким email уже существует"
    error_code = "user_already_exists"
    status_code = 400