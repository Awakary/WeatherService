import re
from typing import Annotated

from fastapi import HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from authorazation.jwt_token import verify_jwt_token, get_token
from exceptions import ExceptionWithMessage, NotSamePasswordException, UsernamePasswordException
from pd_models import UserCheck, UserInDB, FormDataCreate
from sessions import UserDao

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user(login: str):
    user = UserDao().get_user(login)
    if user:
        return UserInDB(login=user.login, hashed_password=user.password, id=user.id)


def authenticate_user(login: str, password: str) -> UserCheck:
    user = get_user(login)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return user


def get_current_user(token: Annotated[str, Depends(get_token)]) -> UserInDB:
    decoded_data = verify_jwt_token(token)
    if not decoded_data:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = get_user(decoded_data["sub"])
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return user


def validate_password_username(data: Annotated[FormDataCreate, Form()], errors: list = []) -> list:
    # Регулярное выражение для проверки, что строка содержит только латинские символы и цифры
    if errors is not None:
        errors = []
    latin_regex = r'^[A-Za-z0-9]+$'
    if data.password != data.repeated_password:
        errors.append(NotSamePasswordException())
    elif (not re.match(latin_regex, data.login) or not re.match(latin_regex, data.password)
          or not re.match(latin_regex, data.repeated_password)):
        errors.append(UsernamePasswordException())
    return errors
