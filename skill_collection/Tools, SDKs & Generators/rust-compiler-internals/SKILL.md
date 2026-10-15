---
name: "rust-compiler-internals"
description: "Understand Rust compiler internals and rustc usage. Use when optimizing build times, understanding compiler errors, using codegen options, setting up PGO, or contributing to Rust."
---

# Rust Compiler Internals

Guide to rustc flags and codegen knobs based on The rustc Book. For measurement-first performance work, prefer the **rust-performance** skill; use this skill when you need accurate rustc/Cargo flag semantics.

## When to Use This Skill

- Interpreting or setting rustc codegen flags (`-C …`)
- Tuning Cargo `[profile.*]` keys that map to those flags
- Setting up profile-guided optimization (PGO)
- Understanding LTO / codegen-units / panic strategy trade-offs
- Contributing to or reading about rustc (see rustc-dev-guide)

## Triage: when to touch these knobs

| Situation | Prefer |
|-----------|--------|
| “Is my program slow?” / allocations / algorithms | **rust-performance** (measure first) |
| Release binary still hot after profiling points at codegen | `[profile.release]` `lto`, `codegen-units`, then re-bench |
| Binary size | `opt-level = "s"`/`"z"`, `panic = "abort"`, `strip`, LTO |
| Compile time too high | Raise `codegen-units`, disable fat LTO, reduce debuginfo; see rust-performance compile-times |
| PGO | Only after a stable release benchmark loop exists; see `references/pgo.md` |
| Target CPU features | `-C target-cpu=…` when deployment CPU is known |

Default release profile is already fairly strong (`opt-level = 3`). Change one knob at a time and benchmark.

## Cargo profile keys (preferred interface)

```toml
[profile.release]
opt-level = 3
lto = "thin"          # false | "thin" | true | "fat" | "off"
codegen-units = 1
panic = "unwind"      # or "abort"
debug = false
strip = "none"        # "debuginfo" | "symbols"
```

Details: `references/codegen.md`, `references/lto.md`.

## rustc `-C` equivalents

```bash
RUSTFLAGS="-C opt-level=3 -C lto=thin -C codegen-units=1" cargo build --release
RUSTFLAGS="-C target-cpu=native" cargo build --release
```

## Profile-Guided Optimization (PGO)

Use instrumented **release** builds, merge with `llvm-profdata`, then `-C profile-use=…`. Do not invent rustup “profile” subcommands.

```bash
rustup component add llvm-tools-preview
# see references/pgo.md for the full Cargo workflow
```

## Reference Map

- `references/codegen.md` — `opt-level`, `codegen-units`, debuginfo, panic
- `references/lto.md` — LTO modes and Cargo keys
- `references/pgo.md` — Profile-guided optimization
- `references/targets.md` — Target / CPU options

## Key References

- [The rustc Book](https://doc.rust-lang.org/rustc/index.html)
- [PGO](https://doc.rust-lang.org/rustc/profile-guided-optimization.html)
- [Cargo Profiles](https://doc.rust-lang.org/cargo/reference/profiles.html)
- [Guide to Rustc Development](https://rustc-dev-guide.rust-lang.org/)
