---
name: "devops-code"
description: "Code 阶段 DevOps 基础设施管理。项目脚手架初始化、编码规范工具链配置、pre-commit 设置、CI lint 门禁规则。"
---

# devops-code

> **⚠ 硬约束：先配置 → 再验证 → 后使用**
> 加载此 Skill 后，必须按下方工作流从头到尾逐行执行命令。
> 标有"必须执行，不可跳过"的步骤是强制性的，AI 不得合并、跳过或提前执行后续步骤。

## 职责

本 skill 管理从"开发人员写代码"到"代码入库"之间的**基础设施**，不涉及具体功能开发：

| 职责 | 说明 |
|------|------|
| 项目脚手架 | 新项目/子模块初始化：目录结构、`pyproject.toml` 标准化、`uv` 环境搭建 |
| 编码规范配置 | `ruff` ruleset 初始化、`mypy` 配置、编辑器设置同步 |
| Pre-commit 配置 | `pre-commit` hooks 初始化、钩子规则管理 |
| CI 代码门禁 | CI 中 lint/typecheck 的规则配置（不涉及 CI pipeline 部署本身） |
| 规范合规验证 | 项目是否遵守约定的结构和规范（可调用 `code-audit` 执行具体审计） |

**不是**本 skill 的职责：
- 代码质量审计本身（交由 `code-audit`）
- Git 提交规范（交由 `devops-commit`）
- 代码审查流程（交由 `devops-review`）
- 发布流程（交由 `devops-release`）

## 工作流

### 0. 先决条件

```bash
which uv && uv --version
which ruff && ruff --version
which pre-commit && pre-commit --version
```

### 1. 项目脚手架初始化

**必须执行，不可跳过**

```bash
# 初始化 uv 项目
uv init --lib <project_name>
# 或对于已有项目，检查 pyproject.toml 完整性
```

检查以下标准结构是否存在：

```
<project>/
  src/
    <package>/
      __init__.py
  tests/
    __init__.py
    conftest.py
  pyproject.toml
  README.md
```

### 2. 编码规范工具链配置

**必须执行，不可跳过**

添加 dev 依赖：

```bash
uv add --dev ruff mypy pre-commit
```

创建 `pyproject.toml` 中的 ruff 配置段（如缺失）：

```toml
[tool.ruff]
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP"]
ignore = []

[tool.ruff.format]
quote-style = "double"
```

### 3. Pre-commit 配置

创建 `.pre-commit-config.yaml`（如缺失）：

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

安装 hooks：

```bash
pre-commit install
```

### 4. 规范合规验证

调用 `code-audit` 验证当前项目是否满足编码规范：

```bash
ruff check <source_dir>
ruff format --check <source_dir>
```

如有问题，记录差异并提出修复建议。

### 5. CI 门禁规则配置

在 `.github/workflows/` 下创建或更新 lint 工作流（如 CI 已存在则跳过）：

```yaml
name: lint
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync
      - run: uv run ruff check
      - run: uv run ruff format --check
```
