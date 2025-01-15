import sqlalchemy
import pytest
from sqlalchemy.orm import sessionmaker

from authorization.passwords import get_password_hash
from config import settings
from fastapi.testclient import TestClient
from main import app
from db.models import Base, User
from pd_models import FormDataCreate


@pytest.fixture(scope="module")
def create_test_db():
    engine = sqlalchemy.create_engine(settings.DB_URL)  # для тестов используется тестовая  БД sqlite:///./test_db.db"
    Base.metadata.create_all(engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with session_local() as session:
        user1 = User(login="user1", password=get_password_hash("qwerty1"))
        session.add(user1)
        session.commit()
    try:
        yield
    finally:
        Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def create_authorization():
    client.post("/token", data={"login": "user1", "password": "qwerty1"})
    try:
        yield
    finally:
        client.post("/logout")


client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "<title>Wheather</title>" in response.text
    assert "Авторизоваться" in response.text
    assert "Зарегистрироваться" in response.text


def test_registration(create_test_db):
    response = client.post("/register", data=FormDataCreate(login="usertest", password="123456",
                                                            repeated_password="123456").model_dump())
    assert response.status_code == 200
    assert "<title>Wheather</title>" in response.text
    assert "Авторизоваться" in response.text
    assert "Зарегистрироваться" in response.text


def test_failure_registration(create_test_db):
    response = client.post("/register", data=FormDataCreate(login="usertest1", password="123",
                                                            repeated_password="123").model_dump())
    assert response.status_code == 200
    assert "Регистрация" in response.text
    assert "Длина пароля должна быть не менее 6 символов" in response.text


def test_failure_registration_witn_not_latin_symbols(create_test_db):
    response = client.post("/register", data=FormDataCreate(login="пользователь", password="123456",
                                                            repeated_password="123456").model_dump())
    assert response.status_code == 200
    assert "Регистрация" in response.text
    assert "Имя пользователя и пароль должны содержать только латинские буквы и цифры" in response.text


def test_authorization(create_test_db):
    response = client.post("/token", data={"login": "user1", "password": "qwerty1"})
    assert response.status_code == 200
    assert "<title>Wheather</title>" in response.text
    assert "Пользователь: user1" in response.text
    assert "Найти" in response.text
    assert "Выйти" in response.text
    client.post("/logout")
    r = client.post("/logout")
    assert "Авторизоваться" in r.text
    assert "Зарегистрироваться" in r.text


def test_failure_authorization(create_test_db):
    response = client.post("/token", data={"login": "user2", "password": "1111111"})
    assert response.status_code == 200
    assert "<title>Wheather</title>" in response.text
    assert "Incorrect username or password" in response.text
    assert "Авторизоваться" in response.text
    assert "Зарегистрироваться" in response.text


def test_logout(create_test_db):
    client.post("/token", data={"login": "user1", "password": "qwerty1"})
    response = client.post("/logout")
    assert response.status_code == 200
    assert "<title>Wheather</title>" in response.text
    assert "Авторизоваться" in response.text
    assert "Зарегистрироваться" in response.text


def test_find_locations(create_test_db, create_autorization):
    response = client.get("/locations", params={"city": "Paris"})
    assert response.status_code == 200
    assert "<title>Wheather</title>" in response.text
    assert "Paris" in response.text
    assert "Найденные локации" in response.text
    assert "Найти" in response.text
    assert "Выйти" in response.text
