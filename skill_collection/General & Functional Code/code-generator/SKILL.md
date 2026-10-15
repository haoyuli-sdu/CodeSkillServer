---
name: "code-generator"
description: "根据 leaf Spec 或 design.md 自动生成代码。当用户说\\\"生成代码\\\"、\\\"实现功能\\\"、\\\"写代码\\\"时自动触发。支持 CAF v0.6.5 直接从 Spec 生成。"
---

# Code Generator Skill

根据 **leaf Spec**（推荐）或 design.md（可选）自动生成代码。

> **CAF v0.6.5**: 优先从 `specs/SPEC-*.md` (leaf=true) 直接生成代码；`design.md` 仅在复杂/高风险场景作为可选中间层。

## 触发条件（按优先级）

1. **优先**：leaf Spec 存在 (`specs/SPEC-*.md`, `leaf: true`, `status: ready|done|draft`*)
2. **可选**：`design.md` 存在且 `status: done`
3. 或用户明确要求"生成代码"、"实现功能"

## 前置检查

### 1. Charter Freeze 检查
- 若 `charter.yaml#freeze.frozen: false`，提醒用户先执行 `/charter-freeze`

### 2. 输入源检查

| 输入类型 | 路径 | 检查条件 |
|----------|------|----------|
| **leaf Spec**（推荐） | `specs/SPEC-*.md` | `leaf: true` + `status: ready|done|draft`* |
| **design.md**（可选） | `docs/L3/{function}/design.md` | `status: done` |

> \* **关于 draft 状态**：若 Spec 仍为 `status: draft`，需满足以下条件方可实现：
> - Leaf Checklist 已手动确认（各项无阻塞）
> - 用户明确指定该 Spec
> - 实现完成后应将 Spec 状态更新为 `done`

- 若两者都不存在：提示先完成 `/spec`（生成 leaf Spec）

### 3. 语言配置检查
- 读取 `.agent/config/quality.{language_profile}.yaml`

## 执行步骤

### 1. 读取输入文档

**从 leaf Spec**（推荐路径）:
```
specs/SPEC-{id}.md
├── frontmatter: source_requirements, interfaces, depends_on
├── Implementation Plan（步骤 + 文件列表）
├── Acceptance Tests（验收用例）
└── Interfaces Impact（接口影响）
```

**从 design.md**（可选路径）:
```
docs/L3/{function}/design.md
├── 算法设计
├── 数据结构
└── 接口定义
```

### 2. 确定语言和路径

从 `charter.yaml` 获取：
- `language_profile`（单语言项目）
- 或 `components[*].language_profile`（多组件项目）

输出路径：
- 单语言：`src/`
- 多组件：`apps/{component}/`（如 `apps/api/`, `apps/widget/`）

### 3. 应用代码规范

读取对应语言配置并应用：
- `.agent/config/quality.python.yaml`
- `.agent/config/quality.typescript.yaml`
- `.agent/config/quality.java.yaml`
- `.agent/config/quality.cpp.yaml`
- `.agent/config/quality.swift.yaml`

规范要求：
- 类型注解：按 `{{profile.style.type_annotations}}`
- 文档字符串：按 `{{profile.style.docstrings}}`
- 代码复杂度：≤ 10
- Linter：`{{profile.style.linter}}`

### 4. 生成代码

根据 Implementation Plan 中的 **Files / Modules** 生成代码：
- 遵循 `{{profile.source.structure}}` 组织
- 处理边界情况（参考 Acceptance Tests）
- 符合 `docs/L2/interfaces.md` 接口契约

### 5. 验证生成

- 运行 linter 检查格式
- 验证类型注解覆盖
- 检查圈复杂度

## 输出产物

| 组件 | 输出路径 |
|------|----------|
| api-server | `apps/api/**/*.py` |
| chat-widget | `apps/widget/**/*.tsx` |
| admin-dashboard | `apps/admin/**/*.tsx` |
| 单语言项目 | `src/**/*{{profile.source.extensions}}` |

## 输出格式

```markdown
## 代码生成结果

**输入源**: specs/SPEC-{id}.md 或 design.md
**生成的文件**:
- 文件路径
- 文件路径

**语言配置**: python/typescript
**代码规范**: 遵循 quality.{language}.yaml

**质量检查**:
- Linting: PASS/FAIL
- 类型检查: PASS/FAIL
- 复杂度: 符合/超标

**下一步**:
- 运行 test-generator Skill 生成测试
- 或手动 Review 代码
```

## 接口变更规则

**重要**: 若实现过程中需要新增/修改跨组件接口：
1. 先更新 `docs/L2/interfaces.md`（唯一接口真源）
2. 必要时同步 `docs/architecture/api-spec.md`
3. 再修改 Spec/代码

## 示例调用

```
请根据 specs/SPEC-003.md 生成代码。
遵循 .agent/config/quality.python.yaml。
代码放入 apps/api/ 目录。
```
