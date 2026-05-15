import os
from typing import List, Optional, Union
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from fastapi.testclient import TestClient

# Configuration from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/marketplace")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Model
class ProductDB(Base):
    __tablename__ = "products"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    seller_id = Column(Integer, nullable=False)

# Pydantic Models
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

class ProductResponse(ProductBase):
    id: UUID

    class Config:
        from_attributes = True

# FastAPI App
app = FastAPI(title="Marketplace Product API (Dockerized)")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items", response_model=List[ProductResponse])
def get_items(db: Session = Depends(get_db)):
    return db.query(ProductDB).all()

@app.post("/items", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: ProductCreate, db: Session = Depends(get_db)):
    db_item = ProductDB(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/{item_id}", response_model=ProductResponse)
def get_item(item_id: UUID, db: Session = Depends(get_db)):
    item = db.query(ProductDB).filter(ProductDB.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")
    return item

@app.put("/items/{item_id}", response_model=ProductResponse)
def update_item(item_id: UUID, item_update: ProductUpdate, db: Session = Depends(get_db)):
    db_item = db.query(ProductDB).filter(ProductDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: UUID, db: Session = Depends(get_db)):
    db_item = db.query(ProductDB).filter(ProductDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_item)
    db.commit()
    return None

# Self-tests
def run_tests():
    client = TestClient(app)
    
    # Clear database for tests
    session = SessionLocal()
    session.query(ProductDB).delete()
    session.commit()
    session.close()
    
    print("Running self-tests for Dockerized API...")
    
    # Test Create
    payload = {"name": "Docker Prod", "description": "Desc", "price": 100.0, "quantity": 1, "seller_id": 1}
    res = client.post("/items", json=payload)
    assert res.status_code == 201
    pid = res.json()["id"]
    print("✓ Create product")
    
    # Test Get All
    res = client.get("/items")
    assert res.status_code == 200
    assert len(res.json()) >= 1
    print("✓ Get all products")
    
    # Test Get One
    res = client.get(f"/items/{pid}")
    assert res.status_code == 200
    assert res.json()["name"] == "Docker Prod"
    print("✓ Get one product")
    
    # Test Update
    res = client.put(f"/items/{pid}", json={"name": "Docker Prod Updated"})
    assert res.status_code == 200
    assert res.json()["name"] == "Docker Prod Updated"
    print("✓ Update product")
    
    # Test Delete
    res = client.delete(f"/items/{pid}")
    assert res.status_code == 204
    res = client.get(f"/items/{pid}")
    assert res.status_code == 404
    print("✓ Delete product")
    
    print("All self-tests passed successfully!")

if __name__ == "__main__":
    run_tests()
