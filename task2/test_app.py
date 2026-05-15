import sys
import os
from fastapi.testclient import TestClient
import pytest

# Add the project root to sys.path to allow importing from task1
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from task1.main import app, db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    """Clear the in-memory database before each test."""
    db.clear()
    yield

def test_create_item_success():
    payload = {
        "name": "Test Product",
        "description": "Test Description",
        "price": 100.0,
        "quantity": 10,
        "seller_id": 1
    }
    response = client.post("/items", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert "id" in data

def test_create_item_invalid_data():
    # Invalid price (must be > 0)
    payload = {
        "name": "Bad Product",
        "description": "Desc",
        "price": -10.0,
        "quantity": 10,
        "seller_id": 1
    }
    response = client.post("/items", json=payload)
    assert response.status_code == 422

    # Missing required field
    payload = {"name": "Missing Fields"}
    response = client.post("/items", json=payload)
    assert response.status_code == 422

def test_get_all_items():
    # Create a few items
    client.post("/items", json={"name": "P1", "description": "D1", "price": 10.0, "quantity": 1, "seller_id": 1})
    client.post("/items", json={"name": "P2", "description": "D2", "price": 20.0, "quantity": 2, "seller_id": 1})
    
    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_item_success():
    res = client.post("/items", json={"name": "Find Me", "description": "Desc", "price": 10.0, "quantity": 1, "seller_id": 1})
    item_id = res.json()["id"]
    
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Find Me"

def test_get_item_not_found():
    import uuid
    random_id = str(uuid.uuid4())
    response = client.get(f"/items/{random_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

def test_update_item_success():
    res = client.post("/items", json={"name": "Old Name", "description": "Desc", "price": 10.0, "quantity": 1, "seller_id": 1})
    item_id = res.json()["id"]
    
    update_payload = {"name": "New Name"}
    response = client.put(f"/items/{item_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    assert response.json()["description"] == "Desc" # Should remain unchanged

def test_update_item_not_found():
    import uuid
    random_id = str(uuid.uuid4())
    response = client.put(f"/items/{random_id}", json={"name": "Nobody"})
    assert response.status_code == 404

def test_delete_item_success():
    res = client.post("/items", json={"name": "Delete Me", "description": "Desc", "price": 10.0, "quantity": 1, "seller_id": 1})
    item_id = res.json()["id"]
    
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 204
    
    # Verify deletion
    get_res = client.get(f"/items/{item_id}")
    assert get_res.status_code == 404

def test_delete_item_not_found():
    import uuid
    random_id = str(uuid.uuid4())
    response = client.delete(f"/items/{random_id}")
    assert response.status_code == 404
