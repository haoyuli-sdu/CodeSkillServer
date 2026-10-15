---
name: "migrate-code-to-reactjs"
description: "Use this skill to iteratively migrate existing frontend codebases, especially Vue, Angular, Svelte, legacy JavaScript, or mixed frontend repositories, into a ReactJS application built with Node.js 22, pnpm 10.20, TypeScript, Vite 6.3.5, and React 19.1.0. It supports staged multi-turn migrations with reusable plan/progress checkpoints, dependency cleanup, source-framework mapping, optional module analysis docs under react_migration/docs/analysis, and reset-progress archiving under react_migration/docs/history."
---

# Migrate Code to ReactJS

将现有前端项目逐步迁移到固定目标栈：Node.js 22、pnpm 10.20、TypeScript、Vite 6.3.5、React 19.1.0。这个 skill 面向多轮迁移：先固定边界、目录映射、依赖取舍和验证方式，再按节点迁移页面、路由、状态管理、接口层、样式与构建配置，并持续记录计划、进度、分析与步骤。

## 执行原则

1. 先固定迁移边界、目标栈和验证方式，再写 React 代码。
2. 将新的 React 项目和迁移文档统一放在原项目根目录下的 `react_migration/`，不要把迁移中的目标代码散落到原始源码目录。
3. 将新的业务源码默认写成 `.ts` 或 `.tsx`；不要把 JavaScript 继续作为目标形态，只有工具链或极短期兼容文件才允许例外，并在计划中写清退出路径。
4. 将目标包管理器固定为 pnpm 10.20；不要在目标项目里继续使用 npm 或 Yarn，也不要保留 `package-lock.json`、`yarn.lock`、`.yarn/` 等旧包管理器产物。
5. 将目标构建工具固定为 Vite 6.3.5，并使用 React 插件；不要把 Vue CLI、Angular CLI、SvelteKit、webpack、CRA 或其他旧构建链继续带入目标项目，除非计划明确要求并存期保留。
6. 对外部行为保持兼容优先：
   - 路由结构和页面信息架构
   - API 调用语义和错误处理
   - 权限、认证、国际化、环境变量注入
   - 表单、图表、表格、文件上传等关键交互
   - 布局、导航、懒加载和入口流程
7. 优先复用“跨框架且确实仍需要”的业务依赖；对 Vue、Angular、Svelte、webpack、Yarn 等旧栈强绑定依赖，必须记录替换或清理决策，而不是原样复制。
8. 保持迁移后的目录结构尽量贴近原项目的路由边界、页面分组和业务模块，只在 React/Vite 生态约定明显更合适时才偏离，并记录原因。
9. 每当某个计划节点或子节点在本轮被明确完成，立即在 `react_migration/steps/` 写一份独立记录；未完成节点只更新 `progress.md`，不要伪造完成记录。

## 首次执行

第一次在某个仓库使用该 skill 时，先在原项目根目录下建立固定迁移工作区 `react_migration/`。如果该目录已存在，优先复用，而不是重新选择新目录。`react_migration/` 至少包含：

- `plan.md`
- `dependency-mapping.md`
- `validation.md`
- `progress.md`
- `steps/`
- React 项目源码与配置文件，例如 `package.json`、`tsconfig*.json`、`vite.config.ts`、`index.html`、`src/`、`public/`
- 在分析成本高、会跨多轮复用时增加 `docs/analysis/`
- 在需要归档旧计划和旧进度时使用 `docs/history/`

模板与写法见：

- [references/migration-plan-template.md](references/migration-plan-template.md)
- [references/dependency-migration-log-template.md](references/dependency-migration-log-template.md)
- [references/validation-checklist.md](references/validation-checklist.md)
- [references/execution-loop.md](references/execution-loop.md)
- [references/step-record-template.md](references/step-record-template.md)
- [references/module-analysis-template.md](references/module-analysis-template.md)
- [references/react-target-stack-baseline.md](references/react-target-stack-baseline.md)

首次执行的最小流程：

1. 识别源码框架、构建工具、路由、状态管理、UI 组件库、表单方案、图表/表格依赖、国际化和认证方式；按项目类型读取对应专项参考。
2. 明确迁移输出边界：新的 React/Vite 项目统一写入原项目根目录下的 `react_migration/`，不要混写到原项目其他源码目录。
3. 先写出“原目录 / 路由 / 模块 -> React `src/` 目录 / 页面 / 组件 / service”的结构映射，尽可能保留原项目的信息架构和业务分层。
4. 判断迁移策略：
   - 全量替换
   - 并存迁移
   - 按路由或模块绞杀迁移
   - 先抽取设计系统或服务层，再迁 UI
5. 在 `react_migration/plan.md` 建立迁移计划，拆成有序节点，节点编号必须稳定，例如 `P1`、`P2.3`。
6. 如果项目较大、分析成本高或预计会多次回看原模块，在 `react_migration/docs/analysis/` 为关键模块建立分析文档。
7. 在 `react_migration/dependency-mapping.md` 建立依赖映射，先记录旧框架绑定依赖、构建链依赖、状态管理依赖和高风险 UI 依赖的 React 落地策略。
8. 在 `react_migration/validation.md` 定义每类节点的验证方式。
9. 在 `react_migration/progress.md` 记录当前阶段、已完成节点、阻塞点和下一步。
10. 依据 [references/react-target-stack-baseline.md](references/react-target-stack-baseline.md) 建立或校准目标 `package.json` 与工具链；只保留与目标栈和当前业务范围相关的依赖，不要复制参考项目里的无关包。

## 源框架专项参考

只读取与本轮节点相关的参考文件，避免无关上下文进入窗口：

- Vue 项目：读取 [references/vue-to-react-best-practices.md](references/vue-to-react-best-practices.md)
- Angular 项目：读取 [references/angular-to-react-best-practices.md](references/angular-to-react-best-practices.md)
- Svelte 项目：读取 [references/svelte-to-react-best-practices.md](references/svelte-to-react-best-practices.md)
- 旧 JavaScript / jQuery / webpack / 多脚本前端：读取 [references/legacy-frontend-to-react-best-practices.md](references/legacy-frontend-to-react-best-practices.md)
- 混合仓库：只加载当前节点实际涉及的源框架参考，不要整仓同时加载全部说明

## 分析文档要求

当出现下列任一情况时，在 `react_migration/docs/analysis/` 为模块或主题建立分析文档：

- 原模块行为复杂，单轮内难以完整迁移
- 同一模块预计会跨多轮反复读取
- 涉及路由守卫、布局插槽、状态管理、副作用编排、复杂表单、权限体系、国际化、动态图表、文件上传或设计系统映射等高成本理解区域
- 需要为依赖替换、自实现或结构映射保留长期理由

分析文档规则：

- 使用 Markdown，按模块或主题拆分，不要把大段分析堆进 `plan.md` 或 `progress.md`
- 文件名保持稳定、可搜索，例如 `auth-flow.md`、`dashboard-routing.md`、`P2-form-engine.md`
- 如现有分析文档不够完整，新增补充文档而不是把不相关主题继续塞进同一份文件
- 在 `plan.md`、`progress.md`、步骤记录中引用相关分析文档路径，避免重复分析原代码
- 结构模板见 [references/module-analysis-template.md](references/module-analysis-template.md)

## 重复执行循环

每次重复使用本 skill 时，遵循下面顺序：

1. 如果用户明确要求“重置进度”“重新开始计划”“归档当前计划后重开”等，先执行“重置进度规则”，再继续后续步骤。
2. 读取 `react_migration/progress.md` 和 `react_migration/plan.md`，确认下一个未完成节点。
3. 如当前节点涉及第三方库、框架替换、构建链切换或旧依赖清理，读取 `react_migration/dependency-mapping.md` 的相关条目。
4. 如当前节点涉及高成本历史分析，先读取 `react_migration/docs/analysis/` 的相关文档；如果没有合适文档，先补一份最小分析文档。
5. 只收集当前节点所需的最小上下文：
   - 原框架实现
   - 相关样式和模板
   - 配置、环境变量和接口定义
   - `react_migration/` 中已存在的 React/Vite 代码
6. 只迁移与当前节点相关的原始目录。原项目下可能有很多其他源码目录、资源目录或历史产物目录；除非计划节点明确要求，不要把它们纳入当前迁移范围。
7. 在 `react_migration/` 下实施当前节点迁移，并尽可能保持与原项目相近的路由、页面分组、模块边界和数据流语义。
8. 对复杂模块评估成熟 React 生态库是否值得引入；对简单功能优先保持轻依赖实现，并把取舍写入依赖映射。
9. 对照 [references/react-target-stack-baseline.md](references/react-target-stack-baseline.md) 校准目标工具链，确保目标项目继续保持 `Node 22 + pnpm 10.20 + TypeScript + Vite 6.3.5 + React 19.1.0`。
10. 执行对应验证。
11. 若本轮完成了计划节点或子节点，在 `react_migration/steps/` 新增一份以日期和时间标识的迁移记录；记录中必须包含：
    - 本次迁移对应计划中的哪一部分
    - 分析过程和变更范围
    - 相对于原项目差异性较大的变更
    - 遗留问题和风险
12. 更新 `react_migration/progress.md`、`react_migration/plan.md` 节点状态，以及必要的依赖映射记录和分析文档索引。
13. 明确写出下一次调用本 skill 应该继续的节点编号。

详细循环约束见 [references/execution-loop.md](references/execution-loop.md)。步骤记录模板见 [references/step-record-template.md](references/step-record-template.md)。

## 重置进度规则

仅在用户指令中明确包含“重置进度”语义时触发，不要自行推断。

执行方式：

1. 确保 `react_migration/docs/history/` 存在。
2. 将当前 `react_migration/plan.md` 和 `react_migration/progress.md` 归档到 `react_migration/docs/history/`，文件名前缀使用日期或日期时间，例如 `20260416-plan.md`、`20260416-153045-progress.md`。
3. 新建新的 `react_migration/plan.md` 和 `react_migration/progress.md`。
4. 新文件只保留非常简要的历史信息，例如：
   - 本次重置时间
   - 归档文件路径
   - 重置原因
   - 仍然有效的关键结论或待复核事项
5. 默认不要删除 `dependency-mapping.md`、`validation.md`、`steps/`、`docs/analysis/`；只有用户明确要求时才清理这些内容。

## 步骤记录要求

每一份 `react_migration/steps/` 记录都使用稳定、可排序的文件名，推荐格式：`YYYYMMDD-HHMMSS-<node-id>.md`，例如 `20260411-153045-P2.1.md`。

记录至少包含：

- 记录时间
- 对应计划节点编号与标题
- 本轮迁移目标
- 分析过程
- 变更范围
- 与原项目相比差异较大的设计或行为变化
- 验证结果
- 遗留问题
- 风险判断
- 下一步建议

如果一次完成多个紧密相关的子节点，可以写一份合并记录，但必须在标题和正文中明确覆盖的节点编号。

## 节点设计规则

计划节点要足够小，能在一次上下文内完成并验证。优先使用这些粒度：

- 一个路由组或页面簇
- 一个布局壳层或导航体系
- 一个状态管理模块或共享数据模型
- 一个 API/service 适配层
- 一个复杂表单或上传流程
- 一个图表 / 表格 / 仪表盘模块
- 一个认证、权限或国际化适配层
- 一个构建 / 配置 / 依赖清理节点

避免把整个前端系统写成一个节点。若某节点无法在一轮内完成，拆成：

- 契约梳理
- React 骨架
- 交互和状态迁移
- 样式与行为对齐
- 测试补齐
- 切换与清理

## 依赖迁移记忆

第三方依赖不能只在当轮临时判断。凡是出现下面任一情况，都要在 `react_migration/dependency-mapping.md` 增加或更新条目：

- 原项目强依赖某 Vue、Angular、Svelte、webpack、Babel、Yarn、npm 或旧 React 工具链包
- React 生态中没有完全等价方案
- 需要“自己封装一层”而不是直接替换
- 复杂模块可以显著受益于成熟 React 生态库
- 简单功能明确决定不引入额外依赖
- 存在行为差异、渲染差异、样式差异、打包差异、许可证风险
- 未来多个节点都会复用该映射

每条记录至少写清楚：

- 原依赖名与用途
- React/Vite 落地方案
- 为什么选择 React 生态三方库、自实现、暂时并存或彻底删除
- 不兼容点
- 当前决定
- 示例代码或落地文件位置
- 后续待验证事项

模板见 [references/dependency-migration-log-template.md](references/dependency-migration-log-template.md)。

## 验证要求

迁移必须伴随验证，不允许只完成“模板翻译”或“组件改名”。根据项目类型，从 `react_migration/validation.md` 中至少选择一层：

- `pnpm` 安装和锁文件检查
- TypeScript 类型检查
- Vite 构建
- 路由或页面冒烟验证
- 关键 API 流程对比
- 关键交互或表单回归验证
- 组件测试 / 单元测试
- 手工验收脚本

如果原项目没有测试，先补最小回归护栏，再迁移高风险节点。详细检查项见 [references/validation-checklist.md](references/validation-checklist.md)。

## 目标项目约束

- 新的 React 项目目录名固定为原项目根目录下的 `react_migration/`
- 所有新增 React 代码、Vite 配置、迁移文档和中间产物都放在 `react_migration/` 下
- 在 `react_migration/` 内尽可能保留原项目的路由分组、页面边界、组件分层和服务模块语义
- `react_migration/docs/analysis/` 用于按模块保存高复用分析文档；分析不充分时可追加新的补充文档
- `react_migration/docs/history/` 用于按日期归档旧 `plan.md` 和 `progress.md`
- 目标技术栈固定为：
  - Node.js 22
  - pnpm 10.20
  - TypeScript
  - Vite `^6.3.5`
  - React `^19.1.0`
  - React DOM `^19.1.0`
- 目标 `package.json` 只保留与 React/Vite/TypeScript 目标栈和当前迁移范围相关的依赖；不要直接复制源项目或参考项目中的 UI、图表、组织私有包等无关依赖
