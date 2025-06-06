
from fastapi.testclient import TestClient
from main import app, SessionLocal, Base, engine
import pytest

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    # Recreate all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)

def test_get_classes():
    response = client.get("/classes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_book_class_success():
    payload = {
        "class_id": 1,
        "client_name": "Alice",
        "client_email": "alice@example.com"
    }
    response = client.post("/book", json=payload)
    assert response.status_code == 200
    assert response.json()["client_name"] == "Alice"

def test_book_class_invalid_email():
    payload = {
        "class_id": 1,
        "client_name": "Bob",
        "client_email": "invalid-email"
    }
    response = client.post("/book", json=payload)
    assert response.status_code == 422

def test_book_class_empty_name():
    payload = {
        "class_id": 1,
        "client_name": " ",
        "client_email": "bob@example.com"
    }
    response = client.post("/book", json=payload)
    assert response.status_code == 422

def test_get_bookings_success():
    response = client.get("/bookings", params={"email": "alice@example.com"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_bookings_invalid_email():
    response = client.get("/bookings", params={"email": "invalid-email"})
    assert response.status_code == 400

def test_get_bookings_not_found():
    response = client.get("/bookings", params={"email": "nobookings@example.com"})
    assert response.status_code == 404
