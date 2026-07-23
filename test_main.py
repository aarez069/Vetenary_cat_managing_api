import pytest
from fastapi.testclient import TestClient
from main import app, engine, localsession, base, cat, sessionmaker, create_engine, pre

Database_url = "sqlite:///./test.db"
engine = create_engine(Database_url, connect_args={"check_same_thread": False})
TestLocalSession = sessionmaker(bind=engine, autoflush=False)
base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestLocalSession(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def Client(db_session):
    def override_pre():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[pre] = override_pre
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_view_data(Client):
    response = Client.get("/view")
    assert response.status_code == 404
    assert response.json() == {"detail": "No entries yet!!!"}


def test_add(Client):
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


def test_view_specific(Client):
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


def test_update_cat(Client):
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


def test_delete_cat(Client):
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
