import json

from fastapi import Form
from fastapi.testclient import TestClient

from main import app
from pd_models import FormData


client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_registration():

    response = client.post("/register",
                           data=FormData(login="ty1", password="12345").model_dump(),
                           )
    assert response.json()['login'] == "ty1"
    assert response.status_code == 200