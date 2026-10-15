---
name: "database-schema"
description: "Generate comprehensive database schemas with proper relations, migrations, and ORM/ODM models for PostgreSQL, MongoDB, and SQLite. Use when creating database schemas that integrate with FastAPI applications, including SQLAlchemy models for SQL databases, PyMongo/ODMantic models for MongoDB, Alembic migrations, and proper relationship definitions."
---

# Database Schema Generator

This skill provides comprehensive tools for generating database schemas with proper relations, migrations, and ORM/ODM models for PostgreSQL, MongoDB, and SQLite that integrate seamlessly with FastAPI applications.

## When to Use This Skill

Use this skill when you need to:
- Generate database schemas with proper relationships and constraints
- Create ORM/ODM models for SQL (SQLAlchemy) or NoSQL (ODMantic/PyMongo) databases
- Set up database migrations for schema evolution
- Define proper indexing strategies for performance
- Generate FastAPI integration patterns for database operations
- Create database connection pools and session management

## Supported Database Types

### SQL Databases
- **PostgreSQL**: Advanced features, JSON support, full-text search
- **SQLite**: Lightweight, file-based, perfect for development/testing
- **MySQL**: Traditional SQL with comprehensive feature set (coming soon)

### NoSQL Databases
- **MongoDB**: Document-based with flexible schema and rich query language

## Core Workflow

### 1. Database Type Selection
- Choose between PostgreSQL, MongoDB, or SQLite based on requirements
- Consider factors: scalability, ACID compliance, document flexibility, deployment complexity

### 2. Schema Design
- Define entities and their relationships
- Plan indexes for optimal query performance
- Consider data normalization vs. denormalization trade-offs

### 3. Model Generation
- Create appropriate ORM/ODM models based on database type
- Define proper field types and constraints
- Implement relationship mappings

### 4. Migration Strategy
- Generate migration files for schema evolution
- Plan rollback strategies for safe deployments
- Consider data migration needs

### 5. FastAPI Integration
- Set up database connection pools
- Implement dependency injection for database sessions
- Create proper error handling for database operations

## Database-Specific Patterns

### PostgreSQL Schema Generation

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")

# PostgreSQL-specific indexes
Index('idx_user_email', 'email', unique=True)
Index('idx_user_created_at', 'created_at')
```

### MongoDB Schema Generation (ODMantic)

```python
from odmantic import Model, Field, Index
from datetime import datetime
from typing import List, Optional

class User(Model):
    email: str = Field(unique=True, regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        collection = "users"
        indexes = [
            Index("email", unique=True),
            Index("created_at")
        ]

class Post(Model):
    title: str
    content: str
    author_id: str = Field(foreign_key="User.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Embedded relationships in MongoDB
    tags: List[str] = []
    metadata: Optional[dict] = {}

    class Config:
        collection = "posts"
        indexes = [
            Index("author_id"),
            Index("created_at"),
            Index("tags")
        ]
```

### SQLite Schema Generation

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    posts = relationship("Post", back_populates="author")
```

## Migration Patterns

### Alembic Migration Example

```python
"""Add user profile fields

Revision ID: abc123def456
Revises: 7d5c8b1a2c3d
Create Date: 2023-10-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123def456'
down_revision = '7d5c8b1a2c3d'
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=True, default=False))

    # Create indexes
    op.create_index('ix_users_bio', 'users', ['bio'])
    op.create_index('ix_users_is_verified', 'users', ['is_verified'])

def downgrade():
    # Remove columns (in reverse order)
    op.drop_index('ix_users_is_verified')
    op.drop_index('ix_users_bio')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'bio')
```

## FastAPI Integration Patterns

### Database Dependency

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from database.session import get_db

async def get_current_user(
    token: str = Security(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
```

## Best Practices

### Performance Optimization
- Use proper indexing strategies
- Implement connection pooling
- Use eager loading for related data when needed
- Consider caching strategies for read-heavy operations

### Security Considerations
- Sanitize all database inputs
- Use parameterized queries to prevent injection
- Implement proper authentication and authorization
- Encrypt sensitive data at rest

### Scalability Patterns
- Plan for database sharding if needed
- Use read replicas for read-heavy operations
- Implement proper database connection management
- Consider database-specific optimization techniques

## Advanced Features

### Relationship Handling
- One-to-Many relationships with proper cascading
- Many-to-Many relationships with join tables
- One-to-One relationships for specialized use cases
- Self-referencing relationships for hierarchical data

### Data Validation
- Database-level constraints
- Application-level validation through ORM/ODM
- Custom validation functions
- Data integrity checks

## References
- See [POSTGRESQL.md](references/POSTGRESQL.md) for PostgreSQL-specific patterns
- See [MONGODB.md](references/MONGODB.md) for MongoDB schema design
- See [SQLITE.md](references/SQLITE.md) for SQLite optimization
- See [MIGRATIONS.md](references/MIGRATIONS.md) for migration strategies
- See [RELATIONS.md](references/RELATIONS.md) for relationship patterns
- See [FASTAPI_INTEGRATION.md](references/FASTAPI_INTEGRATION.md) for FastAPI database patterns
