---
name: "react-class-to-hooks-migrator"
description: "Convert React class components to functional components with hooks. Triggers on: 'convert class component to hooks', 'modernize React code', 'rewrite this class component', lifecycle method names (componentDidMount, componentDidUpdate, componentWillUnmount) in code the user wants updated. Do NOT trigger for codebases that are already fully hooks-based."
---

# Class → Hooks Migrator

## Phase 1 — THINK
This migration's real risk isn't syntax — it's that `componentDidUpdate` and `useEffect` have different mental models, and a naive conversion silently introduces stale closures or infinite re-render loops.
- For every class component being converted, list its lifecycle methods and, critically, what each one *depends on reading* (props/state) at the time it runs
- Specifically check `componentDidUpdate` logic that does conditional work based on comparing prev/current props or state — this needs to become a `useEffect` with a carefully chosen dependency array, not a blind "run every update"
- Check for `this.instance` variables that aren't state (timers, subscriptions, mutable refs) — these map to `useRef`, not `useState`, and mixing them up is a common bug source
- Flag any component using legacy lifecycle methods (`componentWillReceiveProps`, `componentWillMount`) — these need a real redesign, not a mechanical hook swap

## Phase 2 — PLAN
For each component, show before starting:
1. State → `useState`/`useReducer` mapping (recommend `useReducer` if there are more than ~3 interdependent state values, since that's where `useState` sprawl gets buggy)
2. Lifecycle → `useEffect` mapping, with the dependency array explicitly reasoned about per effect, not left as an afterthought
3. Instance variables → `useRef` mapping
4. Any behavior that's genuinely ambiguous to convert safely (e.g., subtle timing in `componentDidUpdate`) flagged for the user to confirm intent before converting

## Phase 3 — EXECUTE
- Convert one component at a time, not a batch find-and-replace
- Write `useEffect` dependency arrays that match actual reads inside the effect (don't suppress the exhaustive-deps lint rule to make it "work" — that's how stale closures get reintroduced)
- Preserve exact rendered output and prop API — this is a mechanics change, not a behavior change, unless explicitly asked otherwise

## Verification checklist
- [ ] No stale-closure bugs (test with rapid state changes / interactions)
- [ ] No infinite re-render loops (check dependency arrays against actual `useEffect` body reads)
- [ ] Component's external prop API and rendered output unchanged

## Security Rules (never violate)
- **No `curl | bash`** — Use only `npm install` / `npm uninstall` for package management.
- **No `eval`** — Never use `eval` or equivalent dynamic code execution.
- **No file operations outside project** — Never read, write, or modify files outside the project directory.
- **No secrets in output** — Never print API keys, tokens, or credentials in reports or logs.
- **Backup before destructive ops** — Always create a git commit or stash before rewriting components.
- **Validate before write** — Validate JSX/TSX syntax compiles before declaring a component done.
- **No silent dependency installs** — Tell the user which packages will be installed and get implicit confirmation before running `npm install`.
- **Never change prop API or rendered output** — This is a mechanics change, not a behavior change. Preserve exact prop types and rendered DOM.
