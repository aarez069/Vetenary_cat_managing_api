import pytest
from fastapi.testclient import TestClient
from main import app, engine, localsession, base, cat

Client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_db():
    base.metadata.drop_all(bind=engine)
    base.metadata.create_all(bind=engine)


def test_view_data():
    response = Client.get("/view")
    assert response.status_code == 404
    assert response.json() == {"detail": "No entries yet!!!"}


def test_add():
    response = Client.post(
        "/add/cat",
        json={
            "Name": "Brownie",
            "DOB": "2025-01-21",
            "Issue": "Neutering",
            "Status": "HEALTHY",
            "Gender": "MALE",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "The cat has been added to your database",
        "entry": {
            "ID": 1,
            "Issue": "Neutering",
            "Gender": "male",
            "Status": "healthy",
            "Name": "Brownie",
            "DOB": "2025-01-21",
        },
    }


def test_view_specific():
    response = Client.post(
        "/add/cat",
        json={
            "Name": "Brownie",
            "DOB": "2025-01-21",
            "Issue": "Neutering",
            "Status": "HEALTHY",
            "Gender": "MALE",
        },
    )
    response = Client.get("/view/specific", params={"Name": "Brownie"})
    assert response.status_code == 200
    response_body = response.json()
    assert response_body["Cats"][0]["Name"] == "Brownie"


def test_update_cat():
    response = Client.post(
        "/add/cat",
        json={
            "Name": "Brownie",
            "DOB": "2025-01-21",
            "Issue": "Neutering",
            "Status": "HEALTHY",
            "Gender": "MALE",
        },
    )
    response = Client.put("/update/1", json={"Name": "Brownie the Great"})
    assert response.status_code == 200
    response_body = response.json()
    assert (
        response_body["message"] == "The provided data has been updated successfully!!!"
    )
    assert response_body["Updated Entry"][0]["Name"] == "Brownie the Great"


def test_delete_cat():
    Client.post(
        "/add/cat",
        json={
            "Name": "Brownie",
            "DOB": "2025-01-21",
            "Issue": "Neutering",
            "Status": "HEALTHY",
            "Gender": "MALE",
        },
    )
    response = Client.delete("/delete/1")
    assert response.status_code == 200
    assert response.json() == {"message": "The entry has been deleted!!!"}
    db = localsession()
    data = db.query(cat).filter(cat.ID == 1).all()
    assert data == []
