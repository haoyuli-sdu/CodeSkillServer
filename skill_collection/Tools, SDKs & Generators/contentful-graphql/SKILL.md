---
name: "contentful-graphql"
description: "Design Contentful GraphQL Content API queries that are fast, typed, and maintainable — fragments, polymorphic unions for Topics & Assemblies, complexity budget management, locale-aware querying, codegen, and the patterns that keep the front end honest as the model evolves. Use this skill any time GraphQL queries are being written, refactored, or audited; when query complexity errors come up; when polymorphic section lists are being designed; when the team is choosing between REST and GraphQL; or when codegen breaks. Trigger whenever the question is \"how should this query look\" or \"why is this query slow."
---

# Contentful GraphQL

GraphQL is the default read interface for Contentful-driven front ends. The selection-set discipline pays off in performance, clarity, and a strong contract with the schema. This skill owns query design and codegen.

Pair with `contentful-content-model` (the schema this skill queries), `contentful-react-wrapper` (the consumer of the queries), `contentful-delivery-optimization` (cache shape and complexity budget), `contentful-localization` (locale-aware queries), and `contentful-personalization` if variant-aware fetching enters.

## When to use this skill

- Designing the queries for a new content type or page.
- Refactoring an over-fetching query.
- A complexity-budget error is showing up in production.
- Setting up GraphQL Code Generator for the project.
- Deciding when to use REST instead.
- Polymorphic section lists (Topics & Assemblies in code).
- Locale-aware, draft-aware queries.

## Core posture

- **Ask only for what you render.** GraphQL exists to skip over-fetching; use it.
- **Fragments are the unit of reuse.** A `HeroFields` fragment lives next to the component that consumes it.
- **Polymorphic unions for assemblies.** A page's section list is a union of section types; use inline fragments and an exhaustive section router (see `contentful-react-wrapper`).
- **Codegen, not hand-written types.** GraphQL Code Generator binds the schema to your queries.
- **Complexity is a budget, not a request count.** A deeply nested query can fail where a hundred shallow ones succeed.
- **One client function, two modes.** Preview and Delivery share the query; the call site sets the flag.

## Endpoint and auth

```
POST https://graphql.contentful.com/content/v1/spaces/{spaceId}/environments/{env}
Authorization: Bearer {DELIVERY or PREVIEW token}
Content-Type: application/json

{ "query": "...", "variables": { ... } }
```

Use the same query for Delivery and Preview; pass the appropriate token. For draft state, GraphQL also accepts `preview: true` as an argument on most root fields:

```graphql
query Article($slug: String!, $preview: Boolean) {
  articleCollection(where: { slug: $slug }, preview: $preview, limit: 1) {
    items {
      title
      body { json }
    }
  }
}
```

## Query shape

Two flavors of root field per content type: singular (`hero(id: "...")`) and collection (`heroCollection(where: {...})`).

```graphql
# Singular — when you have the entry id
query HeroById($id: String!, $preview: Boolean) {
  hero(id: $id, preview: $preview) {
    eyebrow
    headline
    subhead
    primaryCta { label href }
    secondaryCta { label href }
  }
}

# Collection — when you're filtering / paginating
query Articles($skip: Int = 0, $limit: Int = 20, $topic: String) {
  articleCollection(
    where: { topicsCollection_exists: true, topicsCollection_some: { slug: $topic } }
    order: publishedAt_DESC
    skip: $skip
    limit: $limit
  ) {
    total
    items {
      sys { id }
      title
      slug
      summary
      publishedAt
      author { name slug }
    }
  }
}
```

Always select `sys { id }` somewhere when you'll need it for revalidation tags or links — the field doesn't come for free.

## Fragments

Co-locate fragments with components. The pattern that scales:

```graphql
# components/blocks/hero.fragment.graphql
fragment HeroFields on Hero {
  __typename
  sys { id }
  eyebrow
  headline
  subhead
  primaryCta { label href }
  secondaryCta { label href }
}
```

Page query reuses fragments:

```graphql
# app/(marketing)/[slug]/page.graphql
query MarketingPage($slug: String!, $preview: Boolean, $locale: String) {
  pageCollection(where: { slug: $slug }, preview: $preview, locale: $locale, limit: 1) {
    items {
      sys { id }
      title
      slug
      sectionsCollection(limit: 20) {
        items {
          ...on Hero { ...HeroFields }
          ...on FaqSection { ...FaqSectionFields }
          ...on RichTextBlock { ...RichTextFields }
          ...on FeatureGrid { ...FeatureGridFields }
        }
      }
      seo { ...SeoFields }
    }
  }
}
```

The `__typename` on each fragment is what the section router (`contentful-react-wrapper`) switches on.

## Polymorphic unions for Topics & Assemblies

The Topics & Assemblies pattern surfaces in GraphQL as polymorphic reference fields. A `Page.sections` field that accepts `Hero | FaqSection | RichTextBlock` becomes:

```graphql
sectionsCollection(limit: 20) {
  items {
    ...on Hero { ...HeroFields }
    ...on FaqSection { ...FaqSectionFields }
    ...on RichTextBlock { ...RichTextFields }
  }
}
```

Two rules:

- Always select `__typename`. The front end's exhaustive switch needs it.
- One fragment per allowed type. Add a new section type to the model, add a new inline fragment here, and add the case to the front-end router. Codegen makes any miss a type error.

## Filtering and ordering

The `where` argument is a structured filter. Common patterns:

```graphql
# Equals
where: { slug: "delaware-c-corp" }

# Boolean
where: { isPublished: true }

# Range / comparison
where: { publishedAt_gte: "2026-01-01T00:00:00Z" }

# In list
where: { sys: { id_in: ["abc", "def"] } }

# Reference field — entry exists
where: { author_exists: true }

# Reference field — by linked entry's field
where: { author: { slug: "alex-doe" } }

# Multi-reference — at least one match
where: { topicsCollection_some: { slug: "formation" } }

# Compound
where: { AND: [
  { audience: "founder" },
  { OR: [{ stage: "pre-seed" }, { stage: "seed" }] }
]}
```

`order` accepts a list of `{field}_ASC` / `{field}_DESC` enum values. Combine with `skip` + `limit` for pagination. Collections expose `total` for page counts.

## Locale-aware queries

GraphQL takes a `locale` argument at the field level on most queries:

```graphql
query Article($slug: String!, $locale: String!, $preview: Boolean) {
  articleCollection(
    where: { slug: $slug }
    locale: $locale
    preview: $preview
    limit: 1
  ) {
    items { title body { json } }
  }
}
```

Locale falls back per the space's locale fallback chain (see `contentful-localization`). For partially-translated content, expect missing values; handle them in the wrapper.

## Codegen

GraphQL Code Generator wires schema + queries → types.

```yaml
# codegen.yml
schema:
  - https://graphql.contentful.com/content/v1/spaces/${CONTENTFUL_SPACE_ID}/environments/master:
      headers:
        Authorization: Bearer ${CONTENTFUL_DELIVERY_TOKEN}

documents:
  - "src/**/*.graphql"
  - "src/**/*.{ts,tsx}"

generates:
  src/lib/contentful/__generated__/graphql.ts:
    plugins:
      - typescript
      - typescript-operations
      - typed-document-node
    config:
      avoidOptionals: false
      maybeValue: T | null
      enumsAsTypes: true
```

Add a script:

```json
// package.json
{
  "scripts": {
    "codegen": "graphql-codegen",
    "codegen:watch": "graphql-codegen --watch"
  }
}
```

Run on schema change, or wire into a pre-commit / CI step. Commit the generated file. A CI check that reruns codegen and fails on diff catches drift.

For the helper:

```ts
// src/lib/contentful/graphql.ts
import { TypedDocumentNode } from "@graphql-typed-document-node/core";
import { print } from "graphql";

export async function contentfulQuery<TResult, TVariables>(
  doc: TypedDocumentNode<TResult, TVariables>,
  variables: TVariables,
  opts: { preview?: boolean; tags?: string[] } = {},
): Promise<TResult> {
  const query = print(doc);
  // ...same fetch as in contentful-react-wrapper, with TypedDocumentNode the call sites are typed end-to-end
}
```

`useQuery`-style typing for free; the call site gets `TResult` without a generic argument.

## Complexity budget

GraphQL on Contentful enforces a query-complexity budget rather than a per-second rate. Cost factors:

- **Depth.** Each level of nesting costs more.
- **Breadth (collection limits).** A collection with `limit: 100` and nested sub-collections multiplies.
- **Field count per item.** Selecting more fields per item adds up.

Symptoms of an over-budget query:

- HTTP 429 with a complexity message.
- Slow tail-latency on cold cache.
- Build-time data fetches taking minutes.

Mitigations:

1. **Slim the selection set.** Drop fields the front end isn't rendering this iteration.
2. **Paginate.** Don't `limit: 1000`. Page in 20–50.
3. **Split queries.** Two parallel queries with shallower selection sets often beat one deep one. Server components let you `await Promise.all([...])`.
4. **Move to REST for outliers.** A bulk listing where you genuinely need every field of every item is sometimes simpler in REST with `?include=2`.
5. **Prefer fragments.** Reuse keeps the field count honest and reviewable.

Source: https://www.contentful.com/developers/docs/references/graphql/ (rate limit and complexity sections).

## REST vs. GraphQL — when to switch

| GraphQL | REST (CDA) |
|---|---|
| Front-end pages, modular block fetches | Bulk export, large include graphs at depth 5+ |
| Typed queries with codegen | Quick scripts where a typed wrapper is overkill |
| Polymorphic section lists | Simple "give me all entries of type X" |
| Locale-aware single-page reads | Sync API integrations |

In most engagements, GraphQL covers ~95% of the front end and REST covers a few admin / sync / bulk paths.

## Caching headers

Contentful's GraphQL endpoint returns `Cache-Control` headers when behind the CDN. Hand control over to Next.js's revalidation:

- **Use tags** for on-demand invalidation (`tags: ["page:home", "hero:abc123"]`).
- **Use a sane time-based fallback** (`revalidate: 3600`) so stale content doesn't sit forever if a webhook is missed.
- **Skip cache in preview** (`cache: "no-store"`).

See `contentful-delivery-optimization` for the cache-design depth.

## Subscriptions / live updates

Contentful exposes GraphQL subscriptions for live updates over WebSockets. Most production reads do not need this — webhooks + revalidation is the canonical loop. Reach for subscriptions only when:

- Building an editor-facing tool that must reflect Contentful state in real time (some App Framework apps).
- A live dashboard (rare).

For everything else, the on-publish webhook → `revalidateTag` → next request hydrates the fresh data is the right pattern.

## Output formats

### Query proposal (per content type / page)

```
# Query: [Name]

## Endpoint
- Delivery / Preview / both

## Operation
{full GraphQL document}

## Fragments referenced
- {fragment} → {file location}

## Variables
| Name | Type | Source | Default |
|---|---|---|---|

## Cache strategy
- Tags: {list}
- Revalidate: {seconds}
- Preview: {behavior}

## Complexity estimate
- Depth: {n}
- Collection limits: {list}
- Estimated cost: {note}

## Front-end consumer
- Component: {path}
- Wrapper: {path}
```

## Common pitfalls

- **Hand-written types.** They lie within a sprint of any model change. Always codegen.
- **`limit` defaulted to ~100 across the app.** Looks fine on dev with 5 entries; explodes in prod. Set deliberate page sizes.
- **Polymorphic queries that grow on every release without codegen guardrails.** New section type added, but the inline-fragments and the front-end switch never updated. Codegen catches the front end; the query won't catch itself. Make adding a section type a checklist of three places to update.
- **Forgetting `__typename` on union members.** Front-end exhaustiveness check fails silently or at runtime.
- **`cache: "force-cache"` in preview.** Editors publish, see no change, file a bug, lose trust. Preview always opts out of cache.
- **Querying for `body` rich text on listing pages.** Heavy. Listings ask for `summary`; detail asks for `body`.
- **Mixing Delivery and Preview tokens in one client.** Pick a per-request flag and route through one helper.

## How this skill relates to others

- The schema being queried → `contentful-content-model`.
- The wrapper that issues these queries → `contentful-react-wrapper`.
- Cache shape and revalidation → `contentful-delivery-optimization` and `contentful-webhooks`.
- Locale handling → `contentful-localization`.
- Variant fetching when personalization is in scope → `contentful-personalization`.
- App Framework apps that consume the same GraphQL schema → `contentful-app-framework`.

## Source material

- GraphQL Content API: https://www.contentful.com/developers/docs/references/graphql/
- GraphQL Code Generator: https://the-guild.dev/graphql/codegen
- TypedDocumentNode: https://github.com/dotansimha/graphql-typed-document-node
- Plugin reference: `../../references/api-surface.md`
