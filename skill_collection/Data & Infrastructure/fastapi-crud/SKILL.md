---
name: "fastapi-crud"
description: "Generate comprehensive FastAPI CRUD operations with models, schemas, routes, and database integration. Use when creating REST API endpoints for database entities with full Create, Read, Update, Delete functionality, including Pydantic schemas, SQLAlchemy models, dependency injection, and proper error handling."
---

# FastAPI CRUD Generator

This skill provides comprehensive tools for generating FastAPI CRUD operations with proper database integration, validation, and error handling.

## When to Use This Skill

Use this skill when you need to:
- Generate complete CRUD endpoints for a new database entity
- Create Pydantic schemas for request/response validation
- Set up SQLAlchemy models with proper relationships
- Implement proper dependency injection and error handling
- Generate complete API documentation with OpenAPI/Swagger

## Core Workflow

### 1. Entity Analysis
- Identify the database entity and its fields
- Determine required validations and constraints
- Define relationships with other entities
- Plan API endpoints and HTTP methods

### 2. Model Generation
- Create SQLAlchemy model with proper field types
- Define table relationships and constraints
- Set up proper indexing for performance

### 3. Schema Creation
- Generate Pydantic schemas for Create, Read, Update operations
- Implement proper validation rules
- Handle sensitive data and security considerations

### 4. Route Implementation
- Create FastAPI route handlers for all CRUD operations
- Implement proper HTTP status codes
- Add dependency injection for database sessions
- Include proper error handling and validation

### 5. Testing and Documentation
- Generate unit tests for all endpoints
- Ensure OpenAPI documentation is comprehensive
- Add proper response models and examples

## FastAPI CRUD Structure

```
project/
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas
├── routes/           # API route definitions
├── database/         # Database configuration
├── dependencies/     # Dependency injection
└── main.py          # FastAPI application
```

## Key Components

### SQLAlchemy Model Template
```python
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class EntityName(Base):
    __tablename__ = "entity_name"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
```

### Pydantic Schemas Template
```python
from pydantic import BaseModel
from typing import Optional

class EntityCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True

class EntityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class EntityResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True
```

### Route Template
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

router = APIRouter()

@router.post("/", response_model=schemas.EntityResponse)
def create_entity(entity: schemas.EntityCreate, db: Session = Depends(database.get_db)):
    db_entity = models.EntityName(**entity.dict())
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity

@router.get("/{entity_id}", response_model=schemas.EntityResponse)
def get_entity(entity_id: int, db: Session = Depends(database.get_db)):
    entity = db.query(models.EntityName).filter(models.EntityName.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@router.put("/{entity_id}", response_model=schemas.EntityResponse)
def update_entity(entity_id: int, entity_update: schemas.EntityUpdate, db: Session = Depends(database.get_db)):
    db_entity = db.query(models.EntityName).filter(models.EntityName.id == entity_id).first()
    if not db_entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    update_data = entity_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_entity, field, value)

    db.commit()
    db.refresh(db_entity)
    return db_entity

@router.delete("/{entity_id}")
def delete_entity(entity_id: int, db: Session = Depends(database.get_db)):
    entity = db.query(models.EntityName).filter(models.EntityName.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    db.delete(entity)
    db.commit()
    return {"message": "Entity deleted successfully"}
```

## Best Practices

### Security Considerations
- Always use dependency injection for database sessions
- Implement proper authentication and authorization
- Validate all input data with Pydantic schemas
- Use parameterized queries to prevent SQL injection
- Implement rate limiting for API endpoints

### Performance Optimization
- Add proper database indexes
- Use pagination for list endpoints
- Implement caching for read-heavy operations
- Use eager loading for related entities when needed

### Error Handling
- Use appropriate HTTP status codes
- Provide meaningful error messages
- Implement custom exception handlers
- Log errors appropriately for debugging

## Advanced Features

### Relationships
When entities have relationships, define them properly in SQLAlchemy models:

```python
# One-to-Many relationship example
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
```

### Database Session Management
Use dependency injection for database sessions:

```python
from sqlalchemy.orm import Session
from .database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## References
- See [FASTAPI.md](references/FASTAPI.md) for comprehensive FastAPI patterns
- See [SQLALCHEMY.md](references/SQLALCHEMY.md) for SQLAlchemy best practices
- See [SCHEMAS.md](references/SCHEMAS.md) for Pydantic schema patterns
- See [TESTING.md](references/TESTING.md) for API testing strategies
