---
name: "code-implementation"
description: "代码实现 - 按照计划步骤编写代码，处理边界条件和异常情况。"
---

# 代码实现

## 概述

按照计划步骤编写代码，处理边界条件和异常情况。

**核心理念**：最小修改，验证有效。

---

## 执行流程

### 1. 任务理解

- 阅读计划中的任务步骤
- 明确要做什么
- 确认涉及的文件

### 2. 边界思考

执行前思考：
- 输入的极端情况
- 可能出的错误
- 如何处理

### 3. 代码编写

- 最小修改原则
- 遵循项目规范
- 添加必要注释

### 4. 验证

- 运行验证命令
- 确认无报错

---

## 边界条件清单

| 类型 | 检查项 |
|------|--------|
| 输入边界 | 空值、极大值、极小值 |
| 类型边界 | 边界类型、超出范围 |
| 状态边界 | 并发、竞态条件 |
| 资源边界 | 内存、连接数 |

---

## 异常处理

| 场景 | 处理方式 |
|------|----------|
| 参数错误 | 明确报错信息 |
| 外部失败 | 降级处理 |
| 超时 | 重试/超时处理 |
| 未知错误 | 捕获并记录 |

---

## 验证方式

| 语言 | 验证命令 |
|------|----------|
| JavaScript/TypeScript | `node --check file.ts` |
| Python | `python -m py_compile file.py` |
| Go | `go build file.go` |

---

## 注意事项

- 不要过度设计
- 最小修改原则
- 完成后必须验证

---

## 前端开发补充

**如果是前端项目，实现前先读取相关文档：**

| 任务类型 | 必读文档 |
|----------|----------|
| UI 页面/组件开发 | `docs/frontend/COMPONENTS.md` + `docs/frontend/STYLING.md` |
| 样式调整 | `docs/frontend/STYLING.md` |
| 使用现有组件 | `docs/frontend/COMPONENTS.md` |
| API 调用 | `docs/frontend/API.md` |
| 整体了解 | `docs/frontend/` 下全部文档 |

**原则：**
- 优先使用 `docs/frontend/COMPONENTS.md` 中已有的组件
- 样式类名遵循 `docs/frontend/STYLING.md` 中的规范
- UI 模式参考 `docs/frontend/UI-PATTERNS.md`
- API 调用方式参照 `docs/frontend/API.md`
