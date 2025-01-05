from typing import Annotated

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from authorazation.jwt_token import verify_jwt_token, get_token
from pd_models import UserCheck, UserInDB
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
    user = get_user(login)  # Получите пользователя из базы данных
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return user


def get_current_user(token: Annotated[str, Depends(get_token)]) -> UserInDB:
    decoded_data = verify_jwt_token(token)
    if not decoded_data:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = get_user(decoded_data["sub"])  # Получите пользователя из базы данных
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    return user
