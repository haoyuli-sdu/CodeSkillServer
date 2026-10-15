---
name: "docker-foundation"
description: "Use to plan Docker images for services — multi-stage builds, small trusted base images, layer caching, non-root runtime, no secrets baked in, .dockerignore, and reproducible tags. For local dev orchestration or production images; does not scaffold application code."
---

# Docker Foundation

## Purpose

Produce container images that are small, reproducible, secure, and cache-efficient — for a backend service and for consistent local/CI environments — without baking in secrets or shipping bloated, root-running images.

## When to Use

- When a service is containerized for deployment, or dev/CI needs reproducible environments.
- **Not** for choosing the deployment target (`deployment-selection`) or scaffolding app code.

## Inputs

- The service's runtime (Node version), build steps, and workspace context (`pnpm-workspaces`/`npm-workspaces`).
- Deployment target expectations (`deployment-selection`, `../../backend/backend-deployment`).

## Discovery Questions

- What is the runtime + exact version, and the build → run split (compile vs serve)?
- Is this a monorepo build (workspace-aware context, pruned dependencies)?
- What must be injected at runtime (config/secrets — never built in)?

## Responsibilities

- Use **multi-stage builds**: a build stage (deps, compile) and a lean **runtime stage** copying only artifacts — no toolchain, dev deps, or source in the final image.
- Pick a **small, trusted, pinned base image** (specific digest/tag, slim/distroless where viable) — `latest` is non-reproducible and a supply-chain risk (`../../security/dependency-security`).
- Order layers for **cache efficiency**: copy manifests + lockfile and install before copying source, so code changes don't bust the dependency layer (monorepo: prune to the target package's deps).
- **Run as non-root**: dedicated user, minimal filesystem permissions.
- **No secrets in the image or build args that persist in layers** — config/secrets injected at runtime (`secrets-management`, `environment-management`); use build secrets mounts if a build needs a token.
- Add a thorough **`.dockerignore`** (node_modules, .git, .env, tests) to shrink context and avoid leaking files.
- Produce **reproducible, meaningful tags** (immutable, e.g. content/commit-based) that `../../backend/backend-deployment` promotes across environments unchanged.

## Required Workflow

1. Define build vs runtime stages.
2. Pick + pin a small trusted base image.
3. Order layers for dependency caching (workspace-pruned in monorepos).
4. Set non-root user + `.dockerignore`.
5. Ensure runtime-injected config/secrets (none baked); define the tagging scheme.

## Decision Rules

- Multi-stage always for compiled/Node services — runtime images carry artifacts, not toolchains.
- Pin base images by digest/specific tag — never `latest` (reproducibility + supply chain).
- Secrets are runtime, never image-layer; a secret in any layer is leaked to anyone with the image.
- One immutable image promoted across environments — differences are runtime config only (`../../backend/backend-deployment`).

## Rules

- No secrets baked into images or persisted build args.
- Non-root runtime.
- Base images pinned; `.dockerignore` present.

## Anti-Patterns

- Single-stage images shipping the full toolchain + source.
- `FROM node:latest` (non-reproducible, unvetted).
- `COPY . .` before installing deps (cache-busting) or without `.dockerignore` (leaks .env/.git).
- Secrets in `ENV`/build args baked into layers.
- Running as root.

## Validation Checklist

- [ ] Multi-stage; lean runtime image.
- [ ] Small trusted base pinned by digest/tag.
- [ ] Layers ordered for dependency caching (workspace-pruned).
- [ ] Non-root user; `.dockerignore` present.
- [ ] No secrets in image/layers; runtime injection only.
- [ ] Reproducible immutable tags.

## Definition of Done

Reproducible multi-stage images on a small pinned base, cache-efficient, non-root, secret-free (runtime-injected config), with a thorough `.dockerignore` and immutable tags ready for promotion across environments.

## Related Skills

`deployment-selection`, `../../backend/backend-deployment`, `secrets-management`, `environment-management`, `pnpm-workspaces`, `npm-workspaces`, `ci-cd`, `../../security/dependency-security`.

## Related Knowledge

`../../../knowledge/` (runtime versions, target constraints).

## Related References

`../../../references/devops/` (Dockerfile patterns, when populated).

## Context Loading Guidance

- **Requires:** runtime + build steps, workspace context, target expectations.
- **Does not require:** app feature code, deployment-target internals.
- **May load:** `secrets-management`, `deployment-selection`.
- **Stop when:** the image design (stages, base, caching, non-root, tags) is recorded.

## Token Efficiency Guidance

The stage/layer plan + base-image + tag scheme is the artifact; don't paste full Dockerfiles into discussion.
