---
name: "write-tests"
description: "编写单元测试或集成测试时使用此 Skill。涵盖测试设计原则、文件组织和命名规范。"
---

编写单元测试或集成测试。

**输入**：用户要求为某个模块编写测试，或描述需要测试的功能。

---

## 设计原则

- **测试代码实现仅作为参考**。需要理解设计意图针对性编写单元测试。如果意图不明确，应当询问用户确认，而不是根据错误的代码实现制作错误的单元测试。
- **理解设计意图时优先阅读项目文档**。项目文档位于 `docs/` 目录下，按模块组织（如 `docs/rpc/`、`docs/microservice/`、`docs/tools/` 等），文档描述了各模块的设计目的、使用方式和行为契约，是编写测试的首要参考。
- 优先测试行为和契约，而非实现细节。
- 测试应当独立、可重复、无副作用残留。

## 写测试的目的

**写测试的首要目的是发现 bug 和验证行为契约，不是让所有测试通过。**

- 测试不通过不代表测试写错了——很可能是源码有 bug。测试的价值在于暴露问题。
- 当测试失败时，**必须报告给用户**，让用户判断是修复源码还是调整测试。不要擅自修改测试来迎合源码实现。
- 不要为了让测试全部通过而删除或跳过暴露 bug 的测试用例。如果某个测试揭示了源码 bug，保留它，标注清楚问题，交给用户决定。

## 文件组织

### 单元测试

- **Co-location**：与源文件同目录，命名 `*.test.ts`
- 示例：

```
src/utility/
  Waiter.ts
  Waiter.test.ts
  QueueExecutor.ts
  QueueExecutor.test.ts
```

### 集成测试

- **模块内集成测试**：在对应模块目录下创建 `test/` 子文件夹，命名 `*.int.test.ts`
- **跨模块集成测试**：放在 `src/test/integration/` 下
- 示例：

```
src/lib/rpc/
  Route.ts
  Route.test.ts                  ← 单元测试
  test/
    Route.int.test.ts            ← RPC 模块集成测试
    PacketHandler.int.test.ts

src/lib/tcp/
  TCPUtility.ts
  TCPUtility.test.ts
  test/
    TCPRoundTrip.int.test.ts     ← TCP 模块集成测试

src/test/
  integration/
    FullStackRpc.int.test.ts     ← 跨模块集成测试
```

### 测试工具

测试工具（mock 实现、内存版基础设施等）放在 `src/test/tools/` 下，按类别分子目录：

```
src/test/tools/
  discovery/
    RamDiscovery.ts
    RamElection.ts
  mock/
    MockConnector.ts
    MockListener.ts
    MockScope.ts
```

## 命名规范

| 类型 | 模式 | 匹配 glob |
|------|------|-----------|
| 单元测试 | `*.test.ts` | `src/**/*.test.ts` |
| 集成测试 | `*.int.test.ts` | `src/**/*.test.ts` |

## 技术栈

- 测试框架：vitest
- 断言库：vitest 内置 `expect`（不要使用 `node:assert/strict`）
- 配置文件：`vitest.config.ts`（位于各 package 根目录）

## 构建隔离

测试文件不能参与构建流程。需要确保：

1. **tsconfig.json** 排除测试文件：
   ```json
   {
     "exclude": ["node_modules", "dist", "src/**/*.test.ts", "src/test"]
   }
   ```

2. **tsconfig.test.json**（新建）包含全部源码，供 ESLint 类型感知检查使用：
   ```json
   {
     "extends": "./tsconfig.json",
     "include": ["src/**/*"],
     "exclude": ["node_modules", "dist"]
   }
   ```

3. **eslint.config.mjs** 为测试文件指定 `tsconfig.test.json`：
   ```js
   {
     files: ['src/**/*.test.ts'],
     languageOptions: {
       parserOptions: {
         project: ['./tsconfig.test.json'],
       },
     },
   }
   ```

4. **vitest.config.ts** 如使用 swc 插件，需显式禁用默认转换：
   ```js
   export default defineConfig({
     esbuild: false,
     oxc: false,
     plugins: [/* swc plugin */],
   })
   ```

## 注意事项

- 每个测试文件顶部需要 `import 'reflect-metadata'`
- 使用 vitest 内置的 `expect` 做断言，不要用 `node:assert/strict`
- 注意 `@scopeClass` 装饰器产生的 Proxy 行为
- 注意泛型类型窄化问题：如 `LifeCycle<WorkerState.Init>` 会将泛型 T 推断为字面量 `1`，导致 `setState(WorkerState.Pending)` 类型不兼容。用 `as number` 或单独的 tsconfig 放宽类型
- TCP 测试注意端口隔离，使用 portRange 避免并行冲突
- Runtime 是全局单例，测试间需要通过 `shutdown()` 重置状态
- `BehaviorSubject` 订阅时会同步触发一次当前值回调，测试中注意这个行为（特别是 `waitFor` 类模式中 `const sub = subject.subscribe(...)` 可能在赋值前被同步调用）
