---
name: "graphql-resolvers"
description: "Implement GraphQL resolver functions for data fetching and mutation handling."
---

# GraphQL Resolvers

## Overview
GraphQL resolvers map schema fields to data fetching logic. This skill should be invoked when building GraphQL APIs that need to connect to databases, external APIs, or any data source.

## Core Principles
- **Field Resolution**: Each field has a resolver function
- **Parent Access**: Resolvers receive parent value for nested fields
- **Async Support**: Resolvers can return promises
- **DataLoader**: Batch and cache data fetching

## Preparation Checklist
- [ ] Understand schema field structure
- [ ] Identify data sources for each field
- [ ] Plan resolver structure
- [ ] Set up DataLoader

## Step-by-Step Process
1. **Define Types**: Create GraphQL types
2. **Map Fields**: Identify resolver needs per field
3. **Implement**: Write resolver functions
4. **Optimize**: Add DataLoader for batching
5. **Mutations**: Handle create/update/delete
6. **Errors**: Implement error handling

## Do's and Don'ts
- ✅ **Do** use DataLoader to prevent N+1
- ✅ **Do** handle null cases properly
- ✅ **Do** return meaningful errors
- ❌ **Don't** make synchronous calls in resolvers
- ❌ **Don't** skip error handling
- ❌ **Don't** duplicate data fetching logic

## Anti-Patterns
- **N+1 Queries**: Not using DataLoader
- **Sync Calls**: Blocking in resolvers
- **No Errors**: Ignoring error handling
- **Duplication**: Repeating logic across resolvers
