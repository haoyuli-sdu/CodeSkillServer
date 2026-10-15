---
name: "fastapi-model"
description: "Generate a SQLAlchemy model with matching Pydantic v2 schemas for FastAPI. Includes relationships, indexes, and the correct from_attributes configuration."
---

# Generate SQLAlchemy Model + Pydantic Schemas

## When to Use

Use this skill when creating a new database model with its Pydantic schemas for a FastAPI project.

## Instructions

1. Read existing models for conventions (Base class, naming, mixins).

2. Generate the SQLAlchemy model:
   - Use appropriate column types
   - Add indexes on frequently queried columns
   - Set `nullable=False` where data is required
   - Add relationship definitions with `back_populates`
   - Add `__repr__` for debugging

3. Generate Pydantic schemas:
   - `Base` schema with shared fields
   - `Create` schema for POST requests
   - `Response` schema with `model_config = ConfigDict(from_attributes=True)`
   - `Update` schema with all fields optional (`field: type | None = None`)
   - Use `Annotated[type, Field(...)]` for validation
   - Use `@field_validator` (v2 syntax)

4. Generate the Alembic migration command:
   ```bash
   alembic revision --autogenerate -m "add <model_name> table"
   alembic upgrade head
   ```
