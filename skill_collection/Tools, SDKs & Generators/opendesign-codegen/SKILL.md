---
name: "opendesign-codegen"
description: "OpenDesign 代码直出指南。当设计师（尤其各社区体验/设计团队）让 AI 工具把需求/设计意图直接做成页面或组件时使用此 skill——AI 应**直接生成符合工程规范的 Vue 3 + OpenDesign 代码**（真实 O 组件 + --o- 设计 token + scoped SCSS + BEM + i18n），渲染出来即设计稿，无需\"先出 HTML 再转代码\"的中间步骤。提供四大约束（视觉 Token / 组件用法 / 布局响应式 / 工程落地）、合规 SFC 起手模板、组件选用速查、生成后自检清单。仅适用于 UI 库为 @opensig/opendesign 的目标仓——生成前先读目标仓根 AGENTS.md + rules/ 按其框架族/i18n/别名/SEO 约定适配。复用 opendesign-tokens 与 opendesign-components，不重复其内容。"
---

# OpenDesign 代码直出指南

设计师用 AI 工具干活时，**AI 直接产出的就是符合工程规范的 Vue 3 + OpenDesign 代码**——渲染出来即设计稿，可直接进生产工程。

> ❌ 不要"先生成 HTML 再转成代码"。
> ✅ 一步到位：直接输出真实 `@opensig/opendesign` 组件 + `--o-` token 的 Vue SFC。

> 本 skill **不重复** Token 表与组件 API，按需链接：
> - 全量 Token（六主题 / 响应式 / 24 栅格 / 色值反查）→ [`../opendesign-tokens/SKILL.md`](../opendesign-tokens/SKILL.md)
> - 46 个组件的 Props/Events/Slots → [`../opendesign-components/SKILL.md`](../opendesign-components/SKILL.md)
> - 想产 Pixso 设计稿而非代码 → [`../opendesign-design/SKILL.md`](../opendesign-design/SKILL.md)

---

## 适用前提：先确认目标仓用 OpenDesign

本 skill 产出的代码要落进各开源社区官网（portal）仓。**并非所有 portal 都用 OpenDesign**——确认前不要动手：

1. **读目标仓根 `AGENTS.md`**（遵循 [agents.md](https://agents.md) 标准，是所有 AI 工具进仓的唯一入口）的 §1 技术栈表，看 `UI 组件库` 行。
2. **是 `@opensig/opendesign`** → 继续用本 skill。
3. **不是**（如 hifloat 用 shadcn-vue + Tailwind、有的用 Element Plus）→ **停**，改用该仓 UI 库的写法，本 skill 不适用。



---

## 🔴 硬规则红线（生成任何代码前必读，最高优先级）

违反任意一条即视为不合规，必须重写：

1. **组件优先**：凡 OpenDesign 有对应控件（按钮 / 卡片 / 表单 / 表格 / 标签 / 分页等），必须用真实组件 `<OButton>` / `<OCard>` / `<OTable>` …，**禁止用原生 `<button>`/`<select>`/手写 div 替代**。
2. **只用 Token 变量**：颜色 / 间距 / 字号 / 行高 / 圆角 / 阴影一律 `var(--o-*)` 或 `var(--o-r-*)`，**禁止硬编码** hex / rgb / px 字号 / px 间距。**颜色必须用语义 token（`--o-color-*`），严禁直接用色板变量**（blue1/gray1 这类，如 `--o-kleinblue-*`/`--o-grey-*`/`--o-brand-*`）。
3. **`<script setup lang="ts">`** + TypeScript：props 用 `defineProps<T>()` 泛型，不用字符串数组式。
4. **无内联 `style="..."`**（动态值等极特殊情况除外并注释）；**无 `!important`**。
5. **BEM 命名 + `<style lang="scss" scoped>`**，嵌套 ≤ 3 层。
6. **不穿透改组件内部**：视觉差异通过组件 `props` 与主题 token 表达，不用 `:deep()` 重写 OpenDesign 组件内部结构。
7. **文案走 i18n**：不写死面向用户的文字，用目标工程的 i18n 方案（如 `t('module.key')`）。

---

## 起手方式

**从合规 SFC 模板开始，不要白手起稿**：复制 [references/starter-page.vue](references/starter-page.vue)，它已示范：`<script setup>` 区块顺序、`@opensig/opendesign` 组件导入、`--o-`/`--o-r-` token、scoped SCSS、响应式、i18n 占位。

### 主题机制（六社区）

主题由**消费工程在初始化时选定**并通过根节点设置，组件与 token 自动适配，生成的页面代码无需关心：

```html
<html data-o-theme="e.light">  <!-- e/a/k/m/g/u . light/dark -->
```

| 社区 | 主题码 | 社区 | 主题码 |
|------|--------|------|--------|
| openEuler | `e` | Mindspore | `m` |
| Ascend | `a` | openGauss | `g` |
| Kunpeng | `k` | openUBMC | `u` |

颜色全用语义 token → 切主题 / 明暗时自动适配，无需为暗色另写样式。

---

## 四大约束总纲

### ① 视觉 Token

- **颜色必须用语义 token**：背景 `--o-color-fill1/2/3`，文字 `--o-color-info1`~`info4`，主色 `--o-color-primary1`，功能色 `--o-color-success/warning/danger1`，边框 `--o-color-control1`，链接 `--o-color-link1`。语义色自带 rgb 包裹，直接 `var(--o-color-fill2)`。
- 🚫 **严禁直接用色板变量**（即 blue1 / gray1 这类原始色阶）：`--o-kleinblue-*`、`--o-blue-*`、`--o-grey-*`、`--o-green-*`、`--o-red-*`、`--o-orange-*`、`--o-brand-*` 等都**只能由语义 token 内部引用，业务代码禁止直接写**。要的是「这个颜色是什么用途」（语义），不是「这是第几号蓝」（色板）。
  - ❌ `color: var(--o-grey-14)` / `background: var(--o-kleinblue-6)`
  - ✅ `color: var(--o-color-info1)` / `background: var(--o-color-primary1)`
- **页面级**字号/行高/间距优先响应式 token：`--o-r-font_size-*` + 配套 `--o-r-line_height-*`、`--o-r-gap-*`（随视口自动缩放，免写 media query）。
- 圆角 `--o-radius-*`、阴影 `--o-shadow-1/2/3`、动效 `--o-duration-*`+`--o-easing-*`。
- ❌ 禁止 `#fff`/`rgb()`、`--o-color-bg1/2/3`（不存在，背景用 `fill*`）、硬编码 `22px`/`32px`。

详表 → [opendesign-tokens](../opendesign-tokens/SKILL.md)。

### ② 组件用法

设计意图直接映射到 OpenDesign 组件（不自造原生替代）：

| 设计意图 | 组件 | 设计意图 | 组件 |
|----------|------|----------|------|
| 按钮 | `OButton` | 表格 | `OTable` |
| 链接 | `OLink` | 分页 | `OPagination` |
| 卡片 | `OCard` | 标签页 | `OTab`+`OTabPane` |
| 标签 | `OTag` | 对话框 | `ODialog` |
| 输入/下拉 | `OInput` / `OSelect`+`OOption` | 图标 | `OIcon` |

选用速查与关键 props/slots → [references/component-cheatsheet.md](references/component-cheatsheet.md)；完整 API → [opendesign-components](../opendesign-components/SKILL.md)。

### ③ 布局与响应式

- 页面级布局用 24 栅格（`--o-r-grid-N` + 水槽 `--o-r-grid-column-gutter`），并排块列数之和 = 断点总列数。
- 断点 Phone ≤840 / Pad 841–1200 / Laptop 1201–1680 / Desktop >1680，响应式 token 自动适配；确需断点时用 `@media`（或目标工程的 `respond-to` mixin）。

### ④ 工程落地

保证代码可直接进生产工程，详见 [references/engineering-rules.md](references/engineering-rules.md)，核心即上方「硬规则红线」。

> ⚠️ **社区差异**：路径别名（如 `~@/`）、i18n 写法、排版 mixin（`@include h3`）、Vue API 是否自动导入（VitePress 显式 import vs Nuxt 自动导入）、SSR/SSG 安全写法等**因目标仓而异**。本 skill 给的是 OpenDesign 通用合规骨架；落地前先按「工作流·步骤 1」读目标仓根 `AGENTS.md` + `rules/` 适配。各 portal 仓如何暴露这些约定，见 portal-workflow 的 `portal-agents-doc` skill。

---

## 工作流

1. **进仓核实目标工程**（强制，先于写代码）：
   - 读目标仓根 `AGENTS.md`（AI 工具唯一入口）→ 按其规范索引 Read 相关 `rules/*.md`。
   - 确认 UI 库是 `@opensig/opendesign`（见上「适用前提」），否则停。
   - 摸清并据此适配：**框架族**（VitePress：Vue API 显式 import；Nuxt：自动导入、`import.meta.client`/`<ClientOnly>`、`useSeoMeta`）、**路径别名**（`~@/`/`@/` 等）、**i18n**（locales 位置与 `t()` 写法，zh/en 同步）、**SEO/GEO 机制**（TDK 由 portal-workflow geo-fix 链路负责，**组件里不要重复注入**）、**样式 rules**（token 用法、`:deep` 策略、SCSS 嵌套上限、是否有 `respond-to` mixin）、**命名约定**。
   - 不确定处用通用写法 + 注释，绝不臆造仓内不存在的目录/机制。
2. **按需读取最新同级 skill**（这些 skill 不定期更新，勿凭记忆写 token 值/组件 API）——用到的才读，用到的版本才读：
   - 用到颜色/间距/字号/圆角等**具体 token 值** → 读 [`../opendesign-tokens/SKILL.md`](../opendesign-tokens/SKILL.md) + 对应主题 `references/tokens-{theme}.md`。
   - 用到**组件的 Props/Events/Slots** → 读 [`../opendesign-components/SKILL.md`](../opendesign-components/SKILL.md) + 对应 `references/{component}.md`。
   - 需要图标/构建/样式等 **CLI 命令**（`gen:icon`/`build-style` 等）→ 读 [`../opendesign-scripts/SKILL.md`](../opendesign-scripts/SKILL.md)。
   - 需对照**设计稿规范**（栅格/断点/组件视觉规格）→ 读 [`../opendesign-design/SKILL.md`](../opendesign-design/SKILL.md)。
   - 本 skill 顶部链接与 `component-cheatsheet.md` 只是索引，**真值以同级 skill 文件为准**。
3. **起手**：复制 `references/starter-page.vue`。
4. **直接写代码**：用真实 `@opensig/opendesign` 组件搭结构，样式全用 `var(--o-*)`/`var(--o-r-*)`，文案走 i18n，列表用 `v-for`+语义 `:key`。
5. **自检**：逐项核对 [references/checklist.md](references/checklist.md)，修正所有违规；对生成的文件跑 Token CLI 扫描确认无捏造或拼错的 token（`node skills/opendesign-tokens/scripts/bin.mjs scan <file> --theme <主题> --strict`）。
6. 交付即生产代码 —— 渲染出来就是设计稿，无中间转换。

---

## 参考文件

- [references/starter-page.vue](references/starter-page.vue) — 合规 SFC 起手模板
- [references/component-cheatsheet.md](references/component-cheatsheet.md) — 设计意图 → OpenDesign 组件速查
- [references/engineering-rules.md](references/engineering-rules.md) — 工程落地约束
- [references/checklist.md](references/checklist.md) — 生成后自检清单
- [references/examples/feature-section.vue](references/examples/feature-section.vue) — 示例：楼层 + 卡片栅格
- [references/examples/list-filter-page.vue](references/examples/list-filter-page.vue) — 示例：带筛选的列表页
