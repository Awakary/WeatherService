import os

import sqlalchemy
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from starlette.staticfiles import StaticFiles
from alembic import command
from alembic.config import Config

from config import settings
from main import app
from pd_models import FormDataCreate
import pytest
from fastapi.testclient import TestClient
from main import app
from models import Base
from router import router
import databases


# def start_application():
#     app = FastAPI()
#     app.include_router(router)
#     app.mount("/static", StaticFiles(directory="static"), name="static")
#     return app

# Устанавливаем `os.environ`, чтобы использовать тестовую БД


TEST_DB_URL = "sqlite:///./test_db.db"

# database = databases.Database(TEST_DB_URL)



@pytest.fixture(scope="module")
def temp_db():
    engine = sqlalchemy.create_engine(TEST_DB_URL)
    Base.metadata.create_all(engine)# Создаем БД
    try:
        yield
    finally:
        Base.metadata.drop_all(engine)

# @pytest.fixture(autouse=True, scope="module")
# def create_test_database():
#     engine = sqlalchemy.create_engine(TEST_DB_URL)
#     Base.metadata.create_all(engine)
#     yield
#     Base.metadata.drop_all(engine)

# engine = create_engine(
#             url=TEST_DB_URL,
#             connect_args={"check_same_thread": False},
#         )
# SessionTesting = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# Создаем фикстуру для тестов
# @pytest.fixture(scope="function")
# def app():
#     # Создаем таблицы в тестовой базе данных
#     Base.metadata.create_all(engine)
#     _app = start_application()
#     yield _app
#     # Удаляем таблицы после тестов
#     Base.metadata.drop_all(engine)


# @pytest.fixture(scope="function")
# def db_session(app: FastAPI):
#     connection = engine.connect()
#     transaction = connection.begin()
#     session = SessionTesting(bind=connection)
#     yield session
#     session.close()
#     transaction.rollback()
#     connection.close()


# def get_db():
#     db = SessionTesting()
#     try:
#         yield db
#     finally:
#         db.close()


# @pytest.fixture(scope="function")
# def client(app: FastAPI, db_session: SessionTesting):
#     def _get_test_db():
#         try:
#             yield db_session
#         finally:
#             pass
#
#     app.dependency_overrides[get_db] = _get_test_db
#     with TestClient(app) as client:
#         yield client

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_registration(temp_db):
    with TestClient(app) as client:
        response = client.post("/register",
                               data=FormDataCreate(login="kracavchik", password="123456",
                                                   repeated_password="123456").model_dump(),
                               )
    assert response.status_code == 200
