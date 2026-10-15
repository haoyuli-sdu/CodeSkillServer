---
name: "project-scaffold"
description: "快速生成项目脚手架，支持 Python、Node.js、React、Vue 等多种项目类型，内置 Spec-Kit Spec-Driven Development 工作流"
---

# Project Scaffold Skill

快速生成标准化的项目初始结构，包含最佳实践配置。支持 **Spec-Driven Development** 工作流。

## 支持的项目类型

- **python** - Python 项目（含虚拟环境、pytest、black 配置）
- **nodejs** - Node.js 项目（含 ESLint、Prettier、Jest）
- **react** - React + Vite 项目
- **vue** - Vue 3 + Vite 项目
- **nextjs** - Next.js 全栈项目
- **fastapi** - FastAPI 后端项目
- **cli** - CLI 工具项目

## 快速开始

### 1. 创建新项目

```bash
# 基础创建
scaffold create react my-app

# 带初始化选项
scaffold create python my-project --git --install --vscode
```

### 2. 使用 Spec-Kit 工作流 (推荐)

```bash
# 进入项目目录
cd my-app

# 初始化 Spec-Kit 工作流
scaffold init-spec-kit

# 然后开始 Spec-Driven Development
/speckit.constitution   # 建立项目原则
/speckit.specify        # 创建功能规范
/speckit.plan           # 制定技术计划
/speckit.tasks          # 生成任务列表
/speckit.implement      # 执行实施
```

## Spec-Kit 工作流详解

### 什么是 Spec-Driven Development?

传统开发：需求 → 编码 → 测试
Spec-Driven：需求 → **规范** → **计划** → **任务** → 实施

规范成为可执行文档，直接指导代码生成。

### 核心命令

| 命令 | 用途 | 阶段 |
|------|------|------|
| `/speckit.constitution` | 建立项目原则和技术偏好 | 0-1 |
| `/speckit.specify` | 从自然语言描述生成功能规范 | 0-1 |
| `/speckit.clarify` | 澄清模糊需求（可选） | 0-1 |
| `/speckit.plan` | 制定技术实施计划 | 0-1 |
| `/speckit.tasks` | 将规范分解为可执行任务 | 0-1 |
| `/speckit.checklist` | 生成质量检查清单（可选） | 0-1 |
| `/speckit.implement` | 执行实施，生成代码 | 实施 |

### 完整工作流示例

```bash
# 1. 创建 React 项目
scaffold create react todo-app --git
cd todo-app

# 2. 初始化 Spec-Kit
scaffold init-spec-kit

# 3. 使用 Claude Code 执行工作流
/speckit.constitution "专注用户体验，使用函数组件和 Hooks，Tailwind CSS 样式"

/speckit.specify "创建一个 Todo List 应用，支持添加/完成/删除任务，本地存储持久化"

/speckit.plan "使用 React + TypeScript + Tailwind CSS，LocalStorage 存储"

/speckit.tasks

/speckit.implement
```

## 使用方法

### 基础用法

```bash
scaffold <type> <name> [options]
```

**Types:**
- `python` - Python 项目
- `nodejs` - Node.js 项目
- `react` - React + Vite 项目
- `vue` - Vue 3 项目
- `fastapi` - FastAPI 后端
- `cli` - CLI 工具

**Options:**
- `--git` - 初始化 git 仓库
- `--install` - 自动安装依赖
- `--vscode` - 生成 VS Code 配置文件

### Spec-Kit 初始化

```bash
scaffold init-spec-kit [--ai claude|copilot|gemini|codebuddy]
```

为已创建的项目添加 Spec-Kit 工作流支持。

## 项目模板说明

### React + Spec-Kit 项目结构

```
my-app/
├── .claude/
│   └── commands/
│       ├── speckit.constitution.md
│       ├── speckit.specify.md
│       ├── speckit.plan.md
│       ├── speckit.tasks.md
│       ├── speckit.implement.md
│       ├── speckit.clarify.md
│       ├── speckit.analyze.md
│       └── speckit.checklist.md
├── .specify/
│   ├── memory/
│   │   └── constitution.md
│   ├── scripts/
│   │   └── bash/
│   │       ├── create-new-feature.sh
│   │       ├── setup-plan.sh
│   │       └── ...
│   └── templates/
│       ├── spec-template.md
│       ├── plan-template.md
│       └── tasks-template.md
├── specs/
│   └── 001-feature-name/
│       ├── spec.md
│       ├── plan.md
│       └── tasks.md
├── src/
│   └── ...
└── package.json
```

## 完整示例：使用 Spec-Kit 开发 Todo App

### Step 1: 创建项目
```bash
scaffold create react todo-app --git --install
cd todo-app
```

### Step 2: 初始化 Spec-Kit
```bash
scaffold init-spec-kit --ai claude
```

### Step 3: 建立项目原则
```
/speckit.constitution 专注简洁的用户体验，使用现代 React 模式
(Hooks, Function Components)，Tailwind CSS 样式，Framer Motion 动画
```

### Step 4: 创建功能规范
```
/speckit.specify 创建一个 Todo List 应用：
- 用户可以添加任务（输入框 + Enter 键）
- 用户可以标记任务完成/未完成
- 用户可以删除任务
- 支持筛选：全部/进行中/已完成
- 数据持久化到 LocalStorage
- 响应式设计，支持移动端
```

### Step 5: 制定技术计划
```
/speckit.plan 使用 React 18 + TypeScript + Vite + Tailwind CSS + Framer Motion
```

### Step 6: 生成任务并实施
```
/speckit.tasks
/speckit.implement
```

## 进阶用法

### 添加新功能
```bash
# 创建新功能分支
.specify/scripts/bash/create-new-feature.sh --name "user-auth"

# 然后使用 Spec-Kit 命令开发
/speckit.specify "添加用户登录功能，支持邮箱和密码"
```

### 质量检查
```
/speckit.checklist
/speckit.analyze
```

## 为什么使用 Spec-Kit?

1. **意图优先** - 先明确"做什么"和"为什么"
2. **规范可执行** - 规范直接指导代码生成
3. **多步细化** - 不是一次性的提示生成
4. **质量保障** - 内置检查清单和质量验证
5. **技术无关** - 规范不绑定具体技术栈

## 学习资源

- [Spec-Kit 官方文档](https://github.github.io/spec-kit/)
- [Spec-Driven Development 指南](https://github.com/github/spec-kit/blob/main/docs/README.md)

---

**提示**: 使用 `scaffold init-spec-kit` 为任何现有项目添加 Spec-Kit 工作流支持！
