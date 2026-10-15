---
name: "code-rule"
description: "代码真实示例优先使用企业级方案（TypeScript + pnpm + Next + Vue + Vite + Tailwind CSS）。在生成可运行代码示例时自动应用。"
---

# 代码示例技术栈规则

## 触发条件

- 仅在需要给出"可运行、真实"的代码示例时应用本规则。
- 概念解释、伪代码或无代码回答时可不强制。

## 默认技术栈优先级

- 语言优先 `TypeScript`，避免默认使用 JavaScript。
- 包管理与命令优先 `pnpm`，不要默认写 `npm`。
- 前端示例优先 `Vue + Vite`（组件、路由、构建与启动命令），样式库优先 `Tailwind CSS`。
- 全栈/服务端示例优先 `Next`（App Router、Route Handlers、Server Actions）。

## 方案选型优先级（企业级）

- 在"可运行"与"可维护"冲突时，默认优先可维护：选择主流、稳定、长期维护活跃的方案。
- 默认优先 LTS 版本与成熟生态，避免冷门、短期维护或实验性依赖作为首选示例。
- 示例结构优先团队协作友好：明确分层、类型边界、可扩展点与可测试入口。
- 涉及线上能力时，默认补齐基础工程能力：错误处理、输入校验、配置化与日志入口。
- 明确回避"玩具式实现"：只演示 happy path 且缺少边界处理/扩展点的方案不作为默认答案。

## 依赖安装镜像规则

- 涉及依赖安装时，默认优先使用淘宝镜像（`https://registry.npmmirror.com`）。
- `pnpm` 仍是默认首选；若用户指定 `yarn` 或 `npm`，也要给出对应镜像优先写法。
- 需要临时切换源时，优先在命令中显式指定或先设置再安装，避免省略镜像导致安装不稳定。

## 输出要求

- 先给最小可运行示例，再补 1-3 句必要说明。
- 命令要可直接执行，尽量包含完整上下文（安装、启动、验证）。
- 同一回答中保持栈一致，避免混用多个无关框架。
- 可运行代码示例默认添加必要注释，优先解释"在做什么"和"为什么这样做"。
- 注释要简洁聚焦，避免逐行复述代码含义的冗余注释。
- 对关键步骤优先注释：依赖安装、启动命令、验证方式、核心逻辑入口。

## 企业级示例最小清单（输出自检）

- 输入校验：关键入参有基本校验与失败分支，不仅展示成功路径。
- 错误处理：包含可预期错误与兜底异常处理，返回信息可定位问题。
- 可配置项：环境差异通过配置/环境变量承载，避免硬编码。
- 可观测入口：至少保留日志或监控埋点入口，便于排障与审计。
- 测试建议：给出最小测试切入点（单测/集成测试至少一项）。

## 冲突与降级

- 若用户明确指定其他技术栈，优先遵循用户要求。
- 若当前项目已有既定栈，优先遵循项目上下文。
- 若用户明确要求官方源或公司私有源，优先遵循其源配置，不强制淘宝镜像。
- 若用户明确要求"纯净代码/无注释"，优先遵循用户要求，仅在必要处补 1 句说明。
- 若用户明确要求"极简版/面试版/教学版"，可降级为轻量实现，但需补 1 句说明其与企业级方案的差异与上线风险。
- 偏离本规则时，先用 1 句说明原因，再给最接近替代示例。

## 命令示例

```bash
# 创建 Vue + Vite + TypeScript 项目骨架（最小可运行起点）
pnpm create vite my-app --template vue-ts
# 进入项目目录，后续安装与启动都在此目录执行
cd my-app
# 安装依赖
pnpm install
# 安装 Tailwind CSS（样式库）
pnpm add -D tailwindcss @tailwindcss/vite
# 启动本地开发服务器（默认会输出访问地址用于验证）
pnpm dev
```

```bash
# 创建 Next + TypeScript 项目（默认使用 App Router）
pnpm create next-app@latest my-next-app --ts
# 进入项目目录
cd my-next-app
# 启动开发环境并验证首页可访问
pnpm dev
```

```bash
# 将 pnpm 默认源切到淘宝镜像，提升安装稳定性与速度
pnpm config set registry https://registry.npmmirror.com
# 安装依赖
pnpm install

# 若用户指定 yarn，使用同样的镜像策略
yarn config set registry https://registry.npmmirror.com
yarn install

# 若用户指定 npm，使用同样的镜像策略
npm config set registry https://registry.npmmirror.com
npm install
```
