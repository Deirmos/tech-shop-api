from backend.core.exceptions.base import AppError

class AuthenticationError(AppError):
    default_message = "Невалидный токен"
    error_code = "authentication"
    status_code = 401
    

class AuthorizationError(AppError):
    default_message = "Недостаточно прав. Требуется роль администратора"
    error_code = "authorization"
    status_code = 403

class InvalidCredentialsError(AppError):
    default_message = "Неверные учетные данные"
    error_code = "invalid_credentials"
    status_code = 401

class UserAlreadyExistsError(AppError):
    default_message = "Пользователь с таким email уже существует"
    error_code = "user_already_exists"
    status_code = 400

class UserDataNotFoundError(AppError):
    default_message = "Учетные данные не найдены"
    error_code = "user_data_not_found"
    status_code = 404