---
name: "migration-generate"
description: "Generate database migrations from schema changes"
---

# Database Migration Generator

I'll analyze schema changes and generate safe, reversible database migrations automatically.

Arguments: `$ARGUMENTS` - model changes, schema files, or migration description

## Migration Philosophy

- **Safety First**: Always reversible migrations
- **Zero Downtime**: Production-safe strategies
- **Data Preservation**: Never lose user data
- **Incremental Changes**: Small, testable migrations

## Token Optimization

**Expected range**: 800–2,000 tokens (initial), 200 tokens (no changes)

**Caching**: Caches database type detection in `.claude/cache/db/db-type.json` for 7 days. Invalidated when schema files change.

**Early exit**: Returns immediately if no schema changes are detected since the last migration.

**Patterns used**: Grep-before-Read, early exit, template-based generation, caching
