---
name: "migrate-code"
description: "Scrape a migration guide or changelog and automatically update the user's code to match the new version. Use when upgrading a framework, moving to a new API version, or replacing a deprecated library."
---

# Olostep Migrate Code

Take the pain out of major version upgrades. Scrape the official migration guide, understand the breaking changes, and refactor the user's codebase automatically.

## When to use

- User provides a URL to a migration guide (e.g., React 18 to 19, Pages to App Router, API v2 to v3)
- User asks to update deprecated code to use the latest patterns
- User wants to audit a file for deprecated methods based on a new release
- User is replacing one library with another (e.g., Moment.js to date-fns)

## Instructions

When the user provides a migration guide URL (via `$ARGUMENTS` or in conversation):

1. Scrape the migration guide using `mcp__olostep__scrape_website` (use `output_format: markdown`).
2. If the guide spans multiple pages, use `mcp__olostep__get_website_urls` or `mcp__olostep__create_map` to find the relevant pages, and `mcp__olostep__batch_scrape_urls` to read them all.
3. Extract the "Before" and "After" patterns, breaking changes, and deprecated methods from the scraped content.
4. Analyze the user's open or selected code files.
5. Apply the necessary changes, explaining exactly what was updated based on the migration guide.

## Real developer workflows

**"Migrate to a new SDK version"**
> "Scrape https://stripe.com/docs/upgrades and update my webhook handler from API version 2022 to 2026."
→ Scrapes the guide → learns the new event payload shapes → rewrites the TypeScript interfaces and handler logic.

**"Framework upgrade"**
> "Read the Next.js 15 migration guide and update my layout.tsx file."
→ Scrapes the URL → identifies that `params` are now asynchronous → refactors the layout component.

**"Replace a deprecated library"**
> "We are moving from Moment.js to date-fns. Scrape the date-fns docs and rewrite this component's date logic."
→ Scrapes the date-fns API reference for equivalent functions → swaps out all Moment.js imports and method calls.

**"API version bump"**
> "Scrape the OpenAI API changelog and update my code from the completions API to the chat completions API"
→ Scrapes the migration docs → identifies the payload and response shape changes → updates the user's code.

## Tips
- Always scrape the docs before writing any code — the migration guide has the exact before/after patterns
- If the migration is complex, break it down step-by-step for the user
- Combine with `/olostep:search` to find the migration guide if the user doesn't have the URL
