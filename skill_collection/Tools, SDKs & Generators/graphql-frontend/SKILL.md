---
name: "graphql-frontend"
description: "Apollo Client setup, colocated fragments, normalized cache, optimistic updates, and graphql-codegen typed hooks."
---

## 1. Trigger Conditions

Invoke this skill when:

- Setting up Apollo Client in a React application
- Writing GraphQL queries, mutations, or fragments
- Debugging cache invalidation or stale data after a mutation
- Setting up `graphql-codegen` for type-safe hooks

## 2. Prerequisites

- Apollo Client installed (`@apollo/client`)
- GraphQL schema available (from the backend or SDL file)
- `graphql-codegen` configured (or to be set up)

## 3. Steps

### Step 1: Query Construction with Fragments
- Query only the exact fields a component needs — no wildcards
- Colocate fragment definitions with the components that consume them:

```ts
// UserProfile.tsx
const USER_PROFILE_FRAGMENT = gql`
  fragment UserProfileFields on User {
    id
    name
    avatarUrl
  }
`;
```

- Always include `id` and `__typename` in every query so Apollo can normalise the cache

### Step 2: Code Generation
- Run `graphql-codegen` to generate fully typed hooks from all `.graphql` files
- Use generated hooks (`useGetUserQuery`, `useUpdateUserMutation`) — never raw `useQuery`/`useMutation` with inline type assertions
- After any schema or operation change: regenerate types

### Step 3: Mutations with Cache Updates
- **Optimistic updates**: implement `optimisticResponse` for mutations that modify UI state instantly
- **New items in lists**: use `cache.modify` to splice new items into the cached list array after a CREATE mutation — it will not happen automatically:

```ts
cache.modify({
  fields: {
    posts(existingPosts = []) {
      return [...existingPosts, newPostRef];
    },
  },
});
```

### Step 4: Error & Loading States
Handle the full triplet on every query: `loading`, `error`, `data`.
Account for partial data errors on non-nullable fields — show graceful fallback UI.

## 4. Anti-Rationalization Table

| Excuse the agent will use | Rebuttal |
|--------------------------|---------|
| "I'll skip `id` and `__typename` in the query — I don't need cache normalisation" | Without them, Apollo can't update the UI when the entity mutates elsewhere. Always include them. |
| "I'll use raw `useQuery<MyType>` instead of the generated hook" | Raw hooks bypass code generation safety. Use the generated hook. |
| "The list will update automatically after the CREATE mutation" | It won't. Apollo doesn't know to add the new item to the list. Use `cache.modify`. |
| "I'll put the fragment at the page level for simplicity" | Page-level fragments accumulate into giant queries. Colocate fragments with their component. |

## 5. Red Flags

Signs this skill is being violated:

- Queries missing `id` or `__typename`
- Raw `useQuery`/`useMutation` used with manual TypeScript type parameters instead of generated hooks
- CREATE mutation not followed by a `cache.modify` or `refetchQueries` call
- Fragment definitions at the top of a page file, not in the consuming component
- `graphql-codegen` not configured or types not regenerated after schema changes

## 6. Verification Gate

Before marking GraphQL frontend work complete:

- [ ] Every query includes `id` and `__typename`
- [ ] `graphql-codegen` configured and types generated
- [ ] Generated hooks used throughout — no raw `useQuery` with type assertions
- [ ] Mutations that create new items update the cache with `cache.modify`
- [ ] Fragments colocated with consuming components
- [ ] Loading, error, and data states all handled in the UI

## 7. References

- [apollo-cache-patterns.md](references/apollo-cache-patterns.md) — Cache normalisation and manual updates
- [codegen-setup.md](references/codegen-setup.md) — graphql-codegen configuration guide
