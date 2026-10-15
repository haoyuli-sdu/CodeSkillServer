---
name: "create-database-migration"
description: "Create or manage Alembic database migrations for schema changes. Use when: adding new database tables, modifying columns, creating indexes, making schema changes, preparing deployment migrations."
---

# Create Database Migration

This skill guides you through creating Alembic database migrations following Wedding Studio conventions.

## Quick Start

Ask one of these:
- *"Create a migration to add a user credits table"*
- *"Add a column to track video generation time"*
- *"Create an index on frequently queried columns"*

## Process

### 1. Modify Your SQLAlchemy Models

First, update your models in `app/models/`:

```python
# app/models/video.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    duration = Column(Integer, default=60)  # New column
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="videos")
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_videos_user_id", "user_id"),
        Index("idx_videos_created_at", "created_at"),
    )
```

### 2. Generate Migration

Use Alembic to auto-generate the migration:

```bash
cd BE-Wedding-Studio
alembic revision --autogenerate -m "Add duration column to videos"
```

This creates a new file in `alembic/versions/`:

```python
# alembic/versions/001_add_duration_to_videos.py
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001abc123'
down_revision = '000xyz789'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add column
    op.add_column('videos', sa.Column('duration', sa.Integer(), nullable=True))
    
    # Set default for existing rows
    op.execute("UPDATE videos SET duration = 60 WHERE duration IS NULL")
    
    # Make NOT NULL
    op.alter_column('videos', 'duration', nullable=False)

def downgrade() -> None:
    op.drop_column('videos', 'duration')
```

### 3. Review & Customize Migration

Always review the generated migration:

```python
# alembic/versions/001_add_duration_to_videos.py
from alembic import op
import sqlalchemy as sa

revision = '001abc123'
down_revision = '000xyz789'

def upgrade() -> None:
    # Add column with default
    op.add_column(
        'videos',
        sa.Column('duration', sa.Integer(), server_default='60', nullable=False)
    )
    
    # Create index for performance
    op.create_index('idx_videos_duration', 'videos', ['duration'])

def downgrade() -> None:
    # Drop in reverse order
    op.drop_index('idx_videos_duration', 'videos')
    op.drop_column('videos', 'duration')
```

### 4. Test Migration Locally

Run the migration on your local database:

```bash
# Apply migration
alembic upgrade head

# Verify changes
psql -U postgres -d wedding_studio -c "SELECT * FROM videos LIMIT 1;"

# Rollback if needed
alembic downgrade -1

# Re-apply
alembic upgrade head
```

### 5. Verify with SQLAlchemy

Make sure your models match the database schema:

```python
# app/models/__init__.py
from sqlalchemy import inspect
from app.database import engine

# This verifies models match database
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Database tables: {tables}")
```

### 6. Add to PR

Include migration file in your PR:
- Path: `alembic/versions/XXXXX_description.py`
- Reference the issue: `Closes #123`
- Document any data migrations needed

## Common Migration Types

### Add a Column

```python
def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('phone_number', sa.String(20), nullable=True)
    )

def downgrade() -> None:
    op.drop_column('users', 'phone_number')
```

### Add a New Table

```python
def upgrade() -> None:
    op.create_table(
        'credits_transaction',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('credits_transaction')
```

### Create an Index

```python
def upgrade() -> None:
    op.create_index(
        'idx_users_email',
        'users',
        ['email'],
        unique=True
    )

def downgrade() -> None:
    op.drop_index('idx_users_email', 'users')
```

### Modify a Column (Nullable)

```python
def upgrade() -> None:
    op.alter_column(
        'videos',
        'description',
        existing_type=sa.String(500),
        nullable=True
    )

def downgrade() -> None:
    op.alter_column(
        'videos',
        'description',
        existing_type=sa.String(500),
        nullable=False
    )
```

### Add a Foreign Key

```python
def upgrade() -> None:
    op.create_foreign_key(
        'fk_videos_user_id',
        'videos', 'users',
        ['user_id'], ['id']
    )

def downgrade() -> None:
    op.drop_constraint('fk_videos_user_id', 'videos', type_='foreignkey')
```

## Best Practices

✅ **Test locally first**: Always test migrations on local database
✅ **Write reversible**: Always implement `downgrade()` function
✅ **Use alembic revision**: Auto-generate, then customize as needed
✅ **One change per migration**: Keep migrations focused and atomic
✅ **Data migrations**: Handle existing data when adding constraints
✅ **Performance**: Create indexes for frequently queried columns
✅ **Document changes**: Add comments explaining why change was needed
✅ **No breaking changes**: Backward compatible for blue-green deployments

## Migration File Structure

```python
"""<description of migration>"""
from alembic import op
import sqlalchemy as sa

# These are auto-generated
revision = '2e4b4e3a5d92'
down_revision = '1e3a3d2c4b81'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Forward migration
    pass

def downgrade() -> None:
    # Reverse migration (must be opposite of upgrade)
    pass
```

## Deploying Migrations

### Development
```bash
alembic upgrade head  # Run all pending migrations
```

### Staging/Production
Migrations run automatically on container startup:

```bash
# In Dockerfile or entrypoint.sh
RUN alembic upgrade head
```

## Troubleshooting

### Migration Won't Apply
```bash
# Check migration history
alembic history

# Check current state
alembic current

# View SQL without applying
alembic upgrade head --sql
```

### Need to Revert
```bash
# Go back one migration
alembic downgrade -1

# Go back to specific revision
alembic downgrade 2e4b4e3a5d92
```

### Data Lost After Migration
Migrations are destructive in downgrade. Always backup before testing:

```bash
# Backup database
pg_dump wedding_studio > backup.sql

# Test migration, then restore if needed
psql wedding_studio < backup.sql
```

## Next Steps

1. ✅ Update SQLAlchemy models
2. ✅ Generate migration: `alembic revision --autogenerate -m "description"`
3. ✅ Review generated migration file
4. ✅ Customize if needed
5. ✅ Test locally: `alembic upgrade head`
6. ✅ Verify schema: `\d+ table_name` (in psql)
7. ✅ Commit migration file
8. ✅ Create PR for review

## Reference

- [Alembic Docs](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Column Types](https://docs.sqlalchemy.org/en/20/core/types.html)
- Backend Instructions: `.github/instructions/backend.instructions.md`
