# Создание и верификация JWT
#
# Используйте библиотеку pyjwt для создания и верификации JWT.
# Сгенерируйте секретный ключ и установите срок действия токена.

from datetime import datetime, timedelta

import jwt
from fastapi import Request, HTTPException, status

SECRET_KEY = "my_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = timedelta(minutes=180)


def create_jwt_token(data: dict):
    expiration = datetime.utcnow() + ACCESS_TOKEN_EXPIRE_MINUTES
    data.update({"exp": expiration})
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_jwt_token(token: str):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_data
    except jwt.ExpiredSignatureError:
        return 'Token is expired'
    except jwt.PyJWTError:
        return None


def get_token(request: Request):
    # достать значение ключа users_access_token из куки
    token = request.cookies.get('user_access_token')
    # if not token:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    return token
