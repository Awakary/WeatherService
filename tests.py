import json
import os
from decimal import Decimal
from unittest.mock import patch

import sqlalchemy
import pytest
from sqlalchemy.orm import sessionmaker

from main import app
from users.authorization.passwords import get_password_hash
from config import settings
from fastapi.testclient import TestClient

from utilites.depends import get_weather_service, get_user_dao, get_location_dao
from db.models import Base, User, Location
from users.schemas import FormDataCreate, LocationCheck, WeatherCheck


class TestCase:
    def __init__(self):
        self.user_dao = get_user_dao()
        self.location_dao = get_location_dao()
        self.weather_service = get_weather_service()


@pytest.fixture(scope="module")
def create_test_db():
    engine = sqlalchemy.create_engine(settings.DB_URL)  # для тестов используется тестовая  БД sqlite:///./test_db.db"
    Base.metadata.create_all(engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with session_local() as session:
        user1 = User(login="user1", password=get_password_hash("qwerty1"))
        session.add(user1)
        session.commit()
        session.refresh(user1)
        location = Location(user_id=user1.id,
                            name='Париж',
                            latitude=Decimal('48.8588897'),
                            longitude=Decimal('2.3200410217200766'),
                            country='FR',
                            state='Ile-de-France')
        session.add(location)
        session.commit()
    try:
        yield
    finally:
        Base.metadata.drop_all(engine)
        try:
            os.remove('test_db.db')
        except Exception as e:
            print(f"Произошла ошибка удаления тестовой БД: {e}")


@pytest.fixture(scope="function")
def create_authorization():
    client.post("/token", data={"login": "user1", "password": "qwerty1"})
    try:
        yield
    finally:
        client.post("/logout")


client = TestClient(app)
test = TestCase()


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
    assert test.user_dao.get_one(login="usertest") is not None


def test_failure_registration_witn_not_latin_symbols(create_test_db):
    response = client.post("/register", data=FormDataCreate(login="пользователь", password="123456",
                                                            repeated_password="123456").model_dump())
    assert response.status_code == 200
    assert "Регистрация" in response.text
    assert "Имя пользователя и пароль должны содержать только латинские буквы и цифры" in response.text
    assert test.user_dao.get_one(login="пользователь") is None


def test_failure_registration_witn_same_login(create_test_db):
    response = client.post("/register", data=FormDataCreate(login="user1", password="123456",
                                                            repeated_password="123456").model_dump())
    assert response.status_code == 200
    assert "Регистрация" in response.text
    assert "Пользователь с таким логином уже существует" in response.text


def test_authorization(create_test_db):
    response = client.post("/token", data={"login": "user1", "password": "qwerty1"})
    assert response.status_code == 200
    assert "<title>Wheather</title>" in response.text
    assert "Пользователь: user1" in response.text
    assert "Найти" in response.text
    assert "Выйти" in response.text
    client.post("/logout")
    response = client.post("/logout")
    assert "Авторизоваться" in response.text
    assert "Зарегистрироваться" in response.text


def test_failure_authorization(create_test_db):
    response = client.post("/token", data={"login": "user2", "password": "1111111"})
    assert response.status_code == 200
    assert "<title>Wheather</title>" in response.text
    assert "Incorrect username or password" in response.text
    assert "Авторизоваться" in response.text
    assert "Зарегистрироваться" in response.text


def test_logout(create_test_db, create_authorization):
    response = client.post("/logout")
    assert response.status_code == 200
    assert "<title>Wheather</title>" in response.text
    assert "Авторизоваться" in response.text
    assert "Зарегистрироваться" in response.text


@patch('requests.get')
def test_find_locations(mock_get):
    # Определяем значение, которое будет возвращаться от апи
    answer_from_api = "fixtures/find_locs_from_openweather_api.json"
    with open(answer_from_api) as f:
        mock_get.return_value.json.return_value = json.load(f)

    mock_get.return_value.status_code = 200
    locations = test.weather_service.find_locations_by_name(city="Сан-Паулу")

    # Проверка, что функция вернула ожидаемые Pydantic объекты
    expected_locations = [
        LocationCheck(
            name='Сан-Паулу',
            lat=Decimal('-23.5506507'),
            lon=Decimal('-46.6333824'),
            country='BR',
            state='São Paulo'),
        LocationCheck(
            name='San Paolo',
            lat=Decimal('38.1278844'),
            lon=Decimal('15.2305908'),
            country='IT',
            state='Sicily')]

    assert locations == expected_locations

    # Убедимся, что requests.get был вызван с правильным URL
    mock_get.assert_called_once_with(test.weather_service.find_locations_url,
                                     params={'q': 'Сан-Паулу',
                                             'appid': settings.WEATHER_API_KEY,
                                             'limit': 5, 'lang': 'ru'})


@patch('requests.get')
def test_weather_for_location(mock_get, create_test_db):
    answer_from_api = "fixtures/get_weather_from_openweather_api.json"
    with open(answer_from_api) as f:
        mock_get.return_value.json.return_value = json.load(f)

    mock_get.return_value.status_code = 200

    current_user = test.user_dao.get_one(login="user1")
    user_locations = test.location_dao.get_all(current_user)
    location_with_weather = test.weather_service.get_user_locations_with_weather(
        user_locations=user_locations)

    expected_location = [
        WeatherCheck(
            location_id=1,
            name='Париж',
            main='Пасмурно',
            temp=5,
            feels_like=1,
            wind_speed=5,
            country='FR',
            state='Ile-de-France'
        )
    ]
    assert location_with_weather == expected_location

    mock_get.assert_called_once_with(test.weather_service.get_weather_url,
                                     params={"lat": Decimal('48.8588897000'),
                                             "lon": Decimal('2.3200410217'),
                                             "appid": settings.WEATHER_API_KEY,
                                             "lang": "ru",
                                             "units": "metric"}
                                     )


@patch('requests.get')
def test_get_locations_page_without_authorization(mock_get, create_test_db):
    answer_from_api = "fixtures/find_locs_from_openweather_api.json"
    with open(answer_from_api) as f:
        mock_get.return_value.json.return_value = json.load(f)
    response = client.get("/locations", params={"city": "Сан-Паулу"})
    assert "Необходимо сначала авторизоваться" in response.text


@patch('requests.get')
def test_read_main_with_authorization(mock_get, create_test_db, create_authorization):
    answer_from_api = "fixtures/get_weather_from_openweather_api.json"
    with open(answer_from_api) as f:
        mock_get.return_value.json.return_value = json.load(f)
    response = client.get("/")
    assert response.status_code == 200
    assert "<title>Wheather</title>" in response.text
    assert "Сохраненные локации" in response.text
    assert "Париж" in response.text
    assert "Пользователь: user1" in response.text
    assert "Выйти" in response.text



def test_add_locations_for_user(create_test_db, create_authorization):
    location = (
        LocationCheck(
            name="Сан-Паулу",
            lat=Decimal("-23.5506507"),
            lon=Decimal("-46.6333824"),
            country="BR",
            state="São Paulo")
    )
    response = client.post("/add_location", data=location.model_dump())
    assert response.status_code == 200
    assert test.location_dao.get_one(name="Сан-Паулу") is not None
    assert "<title>Wheather</title>" in response.text
    assert "Сан-Паулу" in response.text
    assert "Сохраненные локации" in response.text
    assert "Пользователь: user1" in response.text


def test_add_same_location_for_user(create_test_db, create_authorization):
    location = LocationCheck(name='Париж', lat=Decimal('48.8588897'), lon=Decimal('2.3200410217200766'), country='FR',
                             state='Ile-de-France')
    response = client.post("/add_location", data=location.model_dump())
    assert response.status_code == 200
    assert "Location already exists" in response.text


def test_delete_locations_for_user(create_test_db, create_authorization):
    location = test.location_dao.get_one(name="Париж")
    response = client.post("/delete_location", data={"location_id": location.id,
                                                     "location_name": location.name,
                                                     "current_page": 1})
    assert response.status_code == 200
    assert test.location_dao.get_one(name="Париж") is None
    assert "Париж" not in response.text
    assert "Пользователь: user1" in response.text
    assert "Выйти" in response.text
