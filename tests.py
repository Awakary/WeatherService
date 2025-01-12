import sqlalchemy
from pd_models import FormDataCreate
import pytest
from fastapi.testclient import TestClient
from main import app
from models import Base
from router import router
import databases

TEST_DB_URL = "sqlite:///./test_db.db"

@pytest.fixture(scope="module")
def temp_db():
    engine = sqlalchemy.create_engine(TEST_DB_URL)
    Base.metadata.create_all(engine)# Создаем БД
    try:
        yield
    finally:
        Base.metadata.drop_all(engine)


client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_registration(temp_db):
    response = client.post("/register", data=FormDataCreate(login="usertest", password="123456",
                                                            repeated_password="123456").model_dump())
    assert response.status_code == 200
