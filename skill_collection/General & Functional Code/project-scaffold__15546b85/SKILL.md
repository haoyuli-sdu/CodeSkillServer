---
name: "project-scaffold"
description: "Initialize new projects with standard directory structure, config files, and package manager awareness. Use when user says \"初始化项目\", \"搭脚手架\", \"新建项目\", \"scaffold\", \"create new project\", \"init project\", \"帮我建一个新项目\", or mentions starting a fresh project from scratch."
---

# Project Scaffold

Initialize a new project with a consistent, clean structure. Before creating anything, run the environment detection flow — never assume the user's OS, shell, or toolchain.

## Step 1: Understand the project

Ask the user two questions (don't over-ask):
- **Project name** — used as directory name
- **Primary language / stack** — e.g. "Python CLI", "static HTML", "React + Vite", "Node.js backend". If they don't know yet, that's fine — create the minimal structure and adapt later.

## Step 2: Detect environment

Run the detection sequence from `env-adapter`:
- OS / WSL / Container
- Available package managers
- Git status
Return the summary table so the user knows what we're working with.

## Step 3: Create directory structure

```
project/
├── docs/          # 正式文档
├── discuss/       # 讨论草稿、AI 协作记录
├── scripts/       # 启停脚本
├── tests/         # 测试
├── archive/       # 历史版本快照
├── logs/          # 运行日志
└── .vscode/       # (optional) VS Code 配置
```

Add extra dirs based on project type:
- **Python**: `src/<project>/`
- **Node/TS**: keep flat, or `src/` if the framework expects it
- **Static HTML**: only create `public/` instead of `src/`

## Step 4: Create config files

### .editorconfig

Standard settings: LF, UTF-8, 2-space indent, final newline, trim trailing whitespace (except .md).

### .gitattributes

**不要自己写**。去 [gitattributes/gitattributes](https://github.com/gitattributes/gitattributes) 找对应语言的模板（如 `Python.gitattributes`、`Web.gitattributes`），同时合并 `Common.gitattributes`。使用 WebFetch 读取模板内容后拷贝过来。

### .gitignore

**不要自己写**。去 [github/gitignore](https://github.com/github/gitignore) 找对应语言/框架的模板（如 `Python.gitignore`、`Node.gitignore`），同时合并 `Global/` 下适用的编辑器/OS 模板。使用 WebFetch 读取模板内容后拷贝过来。

## Step 5: Bootstrap project files

Based on the detected environment and chosen stack, create the minimal bootstrap files:

- **npm**: `package.json` with `scripts` section (start, test, dev if applicable)
- **uv (Python)**: `pyproject.toml`, then run `uv init` if bare
- **None (static HTML)**: just a minimal `public/index.html`

Don't install dependencies yet — let the user confirm first.

## Step 6: Git init and first commit

```bash
git init
git add -A
git commit -m "chore: scaffold project structure"
```

If the directory is already inside a git repo, skip init and just stage the new files.

## Step 7: Summary

Report:
```
## 项目脚手架已就绪

- 项目路径: /path/to/project
- 目录结构: docs/ discuss/ scripts/ tests/ logs/ archive/
- 脚本类型: .ps1 (Windows) / .sh (WSL)
- 包管理器: uv / npm / bun
- 初次 commit: chore: scaffold project structure

下一步建议:
- 在 discuss/ 下写讨论文档，明确需求和决策
- 完成后在 scripts/ 下创建启停脚本
```
