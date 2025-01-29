from abc import ABC
from typing import Any

from sqlalchemy import create_engine, Row
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from config import settings
from db.models import Location, User
from utilites.exceptions import SameLocationException
from users.schemas import LocationCheckUser, UserInDB


class AbstractDao(ABC):

    def __init__(self, model):
        self.engine = create_engine(
            url=settings.DB_URL,
            echo=False
        )
        self._session_factory = sessionmaker(
            bind=self.engine, autoflush=False
        )
        self._model = model

    def get_one(self, *args, **kwargs):
        ...

    def get_all(self, *args, **kwargs):
        ...

    def save_one(self, *args, **kwargs):
        ...

    def delete_one(self, *args, **kwargs):
        ...


class UserDao(AbstractDao):

    def get_one(self, login: str) -> Row[tuple[User]] | None:
        with self._session_factory() as session:
            user = session.query(self._model).filter(self._model.login == login).first()
        return user

    def save_one(self, login: str, hashed_password: str) -> Row[tuple[User]] | None:
        with self._session_factory() as session:
            new_user = self._model(login=login, password=hashed_password)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
        return new_user


class LocationDao(AbstractDao):

    def get_one(self, name: str) -> Row[tuple[Location]] | None:
        with self._session_factory() as session:
            location = session.query(self._model).filter(self._model.name == name).first()
        return location

    def get_all(self, user: UserInDB) -> list:
        with self._session_factory() as session:
            user_locations = session.query(self._model).filter(self._model.user_id == user.id).all()
            return user_locations

    def save_one(self, location_for_db: LocationCheckUser) -> LocationCheckUser:
        with self._session_factory() as session:
            new_location_dict = location_for_db.model_dump()
            new_location = self._model(**new_location_dict)
            session.add(new_location)
            try:
                session.commit()
            except IntegrityError:
                raise SameLocationException
            session.refresh(new_location)
        return new_location

    def delete_one(self, location_id: int) -> str:
        with self._session_factory() as session:
            session.query(self._model).filter(self._model.id == location_id).delete()
            session.commit()
            return "Удалено"
