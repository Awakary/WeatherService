# Создание и верификация JWT

from datetime import datetime, timedelta

import jwt
from fastapi import Request

SECRET_KEY = "my_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = timedelta(minutes=180)


def create_jwt_token(data: dict) -> str:
    expiration = datetime.utcnow() + ACCESS_TOKEN_EXPIRE_MINUTES
    data.update({"exp": expiration})
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_jwt_token(token: str) -> str | None:
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.ExpiredSignatureError:
        return 'Token is expired'
    except jwt.PyJWTError:
        return None


def get_token(request: Request) -> str:
    # достать значение ключа users_access_token из куки
    return request.cookies.get('user_access_token')
