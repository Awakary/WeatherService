# Создание и верификация JWT

from datetime import datetime, timedelta

import jwt
from fastapi import Request

from config import settings


def create_jwt_token(data: dict) -> str:
    expiration = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expiration})
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def verify_jwt_token(token: str) -> str | None:
    try:
        decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded_data
    except jwt.ExpiredSignatureError:
        return 'Token is expired'
    except jwt.PyJWTError:
        return None


def get_token(request: Request) -> str:
    # достать значение ключа users_access_token из куки
    return request.cookies.get('user_access_token')
