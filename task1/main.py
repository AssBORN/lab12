from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from fastapi.testclient import TestClient

app = FastAPI(title="Marketplace Product API")

# Models
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    seller_id: int = Field(..., gt=0)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)
    seller_id: Optional[int] = Field(None, gt=0)

class Product(ProductBase):
    id: UUID = Field(default_factory=uuid4)

# In-memory database
db: List[Product] = []

@app.get("/items", response_model=List[Product])
async def get_items():
    return db

@app.post("/items", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_item(item: ProductCreate):
    new_item = Product(**item.model_dump())
    db.append(new_item)
    return new_item

@app.get("/items/{item_id}", response_model=Product)
async def get_item(item_id: UUID):
    for item in db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Product not found")

@app.put("/items/{item_id}", response_model=Product)
async def update_item(item_id: UUID, item_update: ProductUpdate):
    for index, item in enumerate(db):
        if item.id == item_id:
            update_data = item_update.model_dump(exclude_unset=True)
            updated_item = item.model_copy(update=update_data)
            db[index] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Product not found")

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: UUID):
    for index, item in enumerate(db):
        if item.id == item_id:
            db.pop(index)
            return
    raise HTTPException(status_code=404, detail="Product not found")

# Self-tests
def run_tests():
    client = TestClient(app)
    db.clear()
    
    print("Running tests...")
    
    # Test Create
    res = client.post("/items", json={"name": "P1", "description": "D1", "price": 10.0, "quantity": 1, "seller_id": 1})
    assert res.status_code == 201
    pid = res.json()["id"]
    print("✓ Create product")
    
    # Test Get All
    res = client.get("/items")
    assert res.status_code == 200
    assert len(res.json()) == 1
    print("✓ Get all products")
    
    # Test Get One
    res = client.get(f"/items/{pid}")
    assert res.status_code == 200
    assert res.json()["name"] == "P1"
    print("✓ Get one product")
    
    # Test Update
    res = client.put(f"/items/{pid}", json={"name": "P1 Updated"})
    assert res.status_code == 200
    assert res.json()["name"] == "P1 Updated"
    print("✓ Update product")
    
    # Test Delete
    res = client.delete(f"/items/{pid}")
    assert res.status_code == 204
    res = client.get(f"/items/{pid}")
    assert res.status_code == 404
    print("✓ Delete product")
    
    # Test Validation
    res = client.post("/items", json={"name": "", "price": -1})
    assert res.status_code == 422
    print("✓ Validation check")
    
    print("All tests passed!")

if __name__ == "__main__":
    run_tests()
