from passlib.context import CryptContext
from async_fastapi_jwt_auth import AuthJWT

from application.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@AuthJWT.load_config
def get_config():
    return settings.jwt.to_dict().items()


def get_password_hash(password: str) -> str:
    """
    Возвращает Hash пароля

    Args:
        password:

    Returns:
        Hash

    """
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    """
    Проверяет пароль на соответствие hash

    Args:
        plain_password: Пароль в открытом виде
        hashed_password: Hash пароля

    Returns:
        Результат проверки

    """
    return pwd_context.verify(plain_password, hashed_password)
