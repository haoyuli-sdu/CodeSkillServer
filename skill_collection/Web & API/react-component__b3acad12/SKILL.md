---
name: "react-component"
description: "Trigger: build or refactor a React component. Use this whenever the user is creating or restructuring a single component — a form, a provider, an error boundary, a .tsx/.jsx file that does too much or mixes data fetching with render — even if they don't say 'component'. Structures ONE component. Reusable multi-part API → react-component-patterns; shared logic → react-hooks."
---

## Activation Contract

Use when creating or refactoring a React component (`.tsx`/`.jsx`) — structure, separation of concerns, naming, hooks placement. Not for performance, testing, or routing.

## Hard Rules

- Split container (owns state/effects) from presentational (pure props → JSX, no data fetching).
- Call hooks only at the top level — never in conditions, loops, or callbacks.
- One component per file; file name and default export match in `PascalCase`.
- Type every prop via a named `Props` type; no implicit `any`.
- Derive values during render; do not mirror props into state.
- Extract a child component or `useX` hook when a component exceeds ~150 lines or mixes two responsibilities.

## Decision Gates

| Situation | Action |
|-----------|--------|
| Fetches data and renders | Split into container + presentational child |
| Stateful logic reused across components | Extract a `useX` custom hook |
| Prop drilling past ~2 levels | Lift to context or colocate state |
| Conditional UI | Early-return guards, not nested ternaries |

## Execution Steps

1. Classify: container or presentational.
2. Define the typed `Props` first.
3. Place hooks at the top in stable order.
4. Keep JSX flat; extract repeated/complex markup into children.
5. Export as default `PascalCase` matching the filename.

```tsx
type GreetingProps = { name: string };
const Greeting = ({ name }: GreetingProps) => <h1>Hello, {name}</h1>;
export default Greeting;
```

## Output Contract

Return:
- Files created/changed, each tagged container or presentational.
- Any custom hook or child component extracted, and why.

## References

- `react-component-patterns` skill — for reusable component APIs (compound, slots, control props, state initializer, extensible styles).
- `ts-function-signatures` skill — for typing the `Props` shape (options object, optional/default props).
- `style-in-regime` skill — for a verdict on whether a style belongs inline or in the project's canonical style unit.
- React docs — Rules of Hooks and component composition (author-time reference).
