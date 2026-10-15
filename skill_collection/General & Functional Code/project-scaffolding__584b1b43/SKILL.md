---
name: "project-scaffolding"
description: "Sets up a new project, service, or module from nothing — structure, tooling, config, and the first working slice — without dragging in machinery it does not need yet. Use this whenever the user starts something new — a new repo, service, CLI, library, package, or a fresh module inside an existing project, including when they just say \"let's build X\" with no code yet. For adding to a codebase that already exists, use feature-implementation."
---

# Project scaffolding

The first hour of a project sets defaults that survive for years. Nobody revisits the test
runner choice or the directory layout once there is code in it — they route around it.

Two opposite failures. **Under-scaffolding**: no tests, no formatter, no CI, and by the time
anyone wants them there are ten thousand lines to retrofit. **Over-scaffolding**: a folder tree
for an architecture the project has not earned, with eleven empty directories and a plugin
system before the first user.

The target: everything needed to work well from day one, nothing that anticipates a problem you
do not have.

## 1. Establish what this actually is

Before choosing anything, settle:

- **What runs it:** CLI, long-running service, library others import, scheduled job, UI?
- **Who consumes it:** you, your team, or the public? Public means versioning and stability
  guarantees from the first release.
- **How long does it live:** a throwaway spike does not need CI, and saying so is legitimate.
- **What is it inside:** a monorepo with existing conventions, or standalone? Existing
  conventions win over any recommendation here.

**Done when:** you can state the project type and its expected lifetime in a sentence.

## 2. Take the ecosystem's default path

Use the standard toolchain for the language unless there is a specific reason not to. A
conventional project is one any newcomer can navigate; a bespoke one costs every future
contributor an afternoon.

Prefer the official initializer where one exists — it stays current with conventions you would
otherwise get subtly wrong. Then read what it produced and delete what does not apply.

Decide, and record in the README:
- Language version, pinned
- Dependency manager, with a committed lockfile
- Test runner
- Formatter and linter (see `code-linting`)
- How to run it locally, in one command

**Done when:** a newcomer could clone and run it from README instructions alone.

## 3. Start flat

Create directories when a file needs one, not before. Three files in one folder is easier to
navigate than three folders with one file each.

Let structure emerge from real pressure: split when a file gets genuinely hard to navigate,
when two things change at different rates, or when a boundary needs enforcing. Layering imposed
on day one encodes a guess about a system that does not exist yet.

The exception: **separate the entry point from the logic immediately.** That one boundary always
pays — it makes the code testable and importable from the start.

**Done when:** every directory that exists has a file in it that needed to be there.

## 4. Build one working slice first

Before the fifth dependency, get one real thing working end to end, one endpoint that returns
a real response, one command that does its job, one function the library exports.

This validates the whole toolchain — build, run, test, import, while it is trivial to fix. A
toolchain problem found after twenty files is a bad afternoon; found now it is a config line.

**Done when:** the slice runs, and a test for it passes.

## 5. Set up the things that are painful to retrofit

Ordered by how much worse they get with delay:

1. **Version control**, with a real `.gitignore` from the start. Committed secrets or build
   artifacts are permanent in history.
2. **Secrets handling** — environment variables and a committed `.env.example`. Never a real
   secret in the repo, not even briefly, not even in a test.
3. **Tests**, one real test, running in one command. The first test is the expensive one; the
   hundredth is free.
4. **Formatter and linter** — trivial now, a thousand-file diff later.
5. **CI**, even just install, lint, test. It is the only thing that keeps the above true.
6. **README** — what it is, how to run it, how to test it. Three sections beat a template.

**Done when:** CI passes on the first commit.

## 6. Defer deliberately, and say so

These are frequently added on day one and almost never needed there: containerization, a
database when a file would do, a message queue, an auth system before a second user, a plugin
architecture, a monorepo tool for one package, an abstraction layer over one implementation.

Each is defensible eventually. None is defensible *before the thing works*. When you skip one,
note it in the README so the omission reads as a decision rather than an oversight.

**Done when:** the deferred list is written down.

## Report

Say what you created, what you chose and why for each tool, the one command to run it, the one
command to test it, and what you deliberately left out. That last part is what stops someone
adding it back next week without knowing it was considered.
