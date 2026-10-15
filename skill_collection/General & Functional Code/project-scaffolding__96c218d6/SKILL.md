---
name: "project-scaffolding"
description: "Use when starting a new SaaS app or adding structure to one — sets up a Next.js (App Router) + TypeScript project with a sane folder layout, path aliases, server/client boundaries, and the conventions the rest of the stack builds on."
---

# Project Scaffolding

## Overview

A SaaS codebase lives or dies by its **boundaries**. Pick **Next.js App Router + TypeScript** and commit to one rule: business logic lives in server-only modules, the UI imports from a typed data-access layer, and secrets never cross into client components. Get the skeleton right and every later skill (auth, billing, jobs) slots in cleanly.

## When to use

- Bootstrapping a new SaaS app from zero.
- An existing app has logic scattered across components and route handlers.
- You need a layout that supports multi-tenancy, billing, and background jobs later.

## Folder layout

```
src/
  app/                      # routes (App Router)
    (marketing)/            # public pages
    (app)/                  # authenticated app, wrapped in a layout that checks session
      [org]/                # tenant-scoped routes (see multi-tenancy)
    api/                    # route handlers (webhooks, integrations)
  server/                   # SERVER-ONLY. never imported by client components
    db/                     # schema + drizzle client (database-schema)
    services/               # business logic, one file per domain
    auth/                   # session helpers (authentication)
  lib/                      # isomorphic helpers (pure, no secrets)
  components/               # UI (ui/* are shadcn primitives)
  env.ts                    # typed env (environment-and-config)
```

## Conventions that pay off

- **`import "server-only"`** at the top of every file in `server/` — turns a leaked import into a build error.
- **Path alias `@/*` → `src/*`** in `tsconfig.json` so imports don't rot.
- **Server Actions for mutations, route handlers for webhooks/integrations.** Don't build a REST layer you don't need.
- **One service per domain** (`server/services/billing.ts`), called by actions and route handlers alike — never duplicate logic in the UI.
- **`strict: true`** plus `"noUncheckedIndexedAccess": true` in tsconfig from day one; retrofitting strictness is misery.

## Recommended baseline

```bash
npx create-next-app@latest --ts --app --tailwind --eslint
# then add: drizzle-orm + drizzle-kit, your auth lib, stripe, zod
```

Keep `next.config` minimal; add `experimental.serverActions` only if your version needs it.

## Pitfalls

- **Putting DB calls in client components** — they can't run there and you'll leak the connection string. Use the data-access layer + server components/actions.
- **A `utils.ts` dumping ground** — split `lib/` (pure) from `server/` (privileged).
- **Deferring `strict` mode** — every week without it adds `any` you'll never remove.
- **Route handlers for everything** — Server Actions are less boilerplate for first-party mutations.
- **No route groups** — mixing marketing and app routes makes auth layouts awkward.

## Hand-off

A typed skeleton with clear server/client boundaries. Next: `environment-and-config` for typed secrets, then `database-schema` to model data.
