import re
from typing import Annotated

from fastapi import HTTPException, Depends, Form
from passlib.context import CryptContext
from starlette import status

from authorization.jwt_token import verify_jwt_token, get_token
from depends import get_user_dao
from utilites.exceptions import (NotSamePasswordException, UsernamePasswordException,
                                 TokenExpiredException, UsernameExistsException)
from schemas import UserCheck, UserInDB, FormDataCreate
from db.sessions import AbstractDao

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user(login: str, dao: Annotated[AbstractDao, Depends()]) -> UserInDB:
    user = dao.get_one(login)
    if user:
        return UserInDB(login=user.login, hashed_password=user.password, id=user.id)


def authenticate_user(login: str, password: str, dao: Annotated[AbstractDao, Depends()]) -> UserCheck:
    user = get_user(login, dao)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return user


def get_current_user(token: Annotated[str, Depends(get_token)],
                     dao: Annotated[AbstractDao, Depends(get_user_dao)]) -> UserInDB:
    decoded_data = verify_jwt_token(token)
    if decoded_data == 'Token is expired':
        raise TokenExpiredException
    if not decoded_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Необходимо сначала авторизоваться")
    user = dao.get_one(decoded_data["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
    return user


def validate_password_username(data: Annotated[FormDataCreate, Form()],
                               dao: Annotated[AbstractDao, Depends()],
                               errors: list = [],) -> list:
    # Регулярное выражение для проверки, что строка содержит только латинские символы и цифры
    if errors is not None:
        errors = []
    latin_regex = r'^[A-Za-z0-9]+$'
    if (not re.match(latin_regex, data.login) or not re.match(latin_regex, data.password)
            or not re.match(latin_regex, data.repeated_password)):
        errors.append(UsernamePasswordException())
    elif data.password != data.repeated_password:
        errors.append(NotSamePasswordException())
    elif dao.get_one(data.login):
        errors.append(UsernameExistsException())
    return errors
