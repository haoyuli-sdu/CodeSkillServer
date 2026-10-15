---
name: "210-java-uniweb-gencode"
description: "Java代码生成与增量更新。当需要为Java后端项目生成或更新代码时触发：(1)首次生成entity/dto/controller, (2)库表变动后增量更新代码并生成变更报告, (3)备份旧文件供后续裁剪恢复。"
---

# Java代码生成

## 项目环境检测

从当前目录向上查找 `project-info.md`，最多 3 层，找到后记为 `PROJECT_ROOT`。详见 [检测方法与前置检查](../0-init/references/project-env-check.md) **第一步、第二步**。**第三步**（uniweb system 环境检测）：从 `~/.uniweb/uniweb-system.config` 读取服务器配置。**未找到** → 提示用户先执行 `0-init`。

## 角色职责

| 角色 | 职责 | 智能体 |
|------|------|--------|
| 主导 | 代码生成 | `java-developer` |


## 初始化流程

**执行前必须询问用户确认**。

### 步骤1: 扫描可用后端项目

**目标目录**：直接使用当前项目根目录（包含 `PROJECT_ROOT/project-info.md` 的目录）。

扫描 `PROJECT_ROOT/backend/` 目录，列出所有可用的后端项目：

```bash
ls -1 PROJECT_ROOT/backend/{project-name}-app/
```

**情况处理**：

| 情况 | 操作 |
|------|------|
| 有后端项目 | 使用 `AskUserQuestion` 让用户选择目标项目 |
| 没有后端项目 | 报错，提示先执行 `210-java-uniweb-init` |

### 步骤2: 询问用户参数

```
AskUserQuestion({
  questions: [
    {
      question: "要为哪个后端项目生成代码？",
      header: "目标后端项目",
      options: [
        { label: "{实际扫描到的项目名}", description: "自动查找可用的后端项目" },
        { label: "手动输入", description: "手动指定后端项目目录名" }
      ],
      multiSelect: false
    },
    {
      question: "要生成的表名（多个用逗号分隔，空表示全部）？",
      header: "表名列表",
      options: [
        { label: "全部表", description: "生成所有表的代码" },
        { label: "手动输入", description: "输入指定的表名，多个用逗号分隔" }
      ],
      multiSelect: false
    },
    {
      question: "需要生成哪些类型？",
      header: "生成类型",
      options: [
        { label: "全部", description: "entity + dto + controller" },
        { label: "entity", description: "实体类" },
        { label: "dto", description: "传输对象" },
        { label: "controller", description: "控制器" }
      ],
      multiSelect: true
    }
  ]
})
```

> **options 规则**：每个问题的 `options` 必须 ≥ 2 项。扫描到项目后，将实际项目名作为第一个选项的 label，同时保留"手动输入"选项。

### 步骤3: 用户确认

**必须**向用户展示以下信息并等待确认：

```
即将执行 Java 代码生成：
- 项目根目录: {当前项目根目录}
- 目标后端项目: {用户选择的后端项目名}
- 表名列表: {用户输入的表名列表}
- 生成类型: {用户选择的类型}

确认执行吗？
```

用户确认后，再执行脚本。

### 步骤4: 执行脚本

用户确认后，执行命令（确保在技能目录下执行）：
```bash
bash scripts/gencode.sh [目标目录] [表名列表] [生成类型] [后端项目名]
```

**参数说明**：

| 参数 | 说明 | 是否必填 | 默认值 |
|------|------|----------|--------|
| 目标目录 | 项目根目录（包含 `PROJECT_ROOT/project-info.md`） | 是 | 当前目录 |
| 表名列表 | 要生成的表名，多个用逗号分隔 | 否 | 全部表 |
| 生成类型 | `entity,dto,controller` 的组合 | 否 | `entity,dto,controller` |
| 后端项目名 | 指定具体的后端项目目录名 | 否 | 自动查找 |

**执行示例**：

```bash
# 生成全部表的全部类型（自动查找后端项目）
bash scripts/gencode.sh /Users/user/project

# 只生成 user 和 order 表的全部类型
bash scripts/gencode.sh /Users/user/project "user,order"

# 全部表，只生成 entity 和 dto
bash scripts/gencode.sh /Users/user/project "" "entity,dto"

# 只生成 user 表的 entity
bash scripts/gencode.sh /Users/user/project "user" "entity"

# 指定后端项目名（多个项目时）
bash scripts/gencode.sh /Users/user/project "" "entity,dto" "my-shop"
```

**脚本输出说明**：
- `✓` 表示通过
- `⚠` 表示警告
- `ERROR` 表示错误，会终止执行

## 生成流程

脚本自动完成：
1. 登录 `uw-auth-center` 获取访问token
2. 调用 `uw-code-center` API 下载代码生成文件（zip），传入 `filterTableNames` 参数
3. 解压代码文件
4. 根据生成类型选择处理：entity、dto、controller
5. 替换包名声明（`package ` → `package {项目包名}.`）
6. 将 entity、dto 移动到项目对应包路径；controller 按 `admin/{module}/` 分包
7. 执行 Maven 编译验证

## 配置项

**从 project-info.md 读取**：

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `project-name` | 项目英文名（短横线分隔） | `my-shop` |

**从 ~/.uniweb/uniweb-system.config 读取**：

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `SYSTEM_SERVER` | 开发服务器地址 | `192.168.88.21` |
| `MSC_OPS_PASSWORD` | ops 用户密码 | `your_password` |

**Schema规则**：项目名中的 `-` 替换为 `_` 作为数据库schema名
- 项目名 `my-shop` → Schema `my_shop`

**包名规则**：项目名中的短横线 `-` 替换为点 `.`
- 项目名 `my-shop` → 包名 `my.shop`

## 输出结构

```
项目根目录/
├── project-info.md
└── PROJECT_ROOT/backend/
    └── {project-name}-app/
        ├── .gencode-backup/              # 增量更新时自动创建
        │   └── {timestamp}/
        │       ├── entity/
        │       ├── dto/
        │       └── controller/           # 按模块子目录备份
        ├── .gencode-diff.md              # 变更报告
        └── src/main/java/{包路径}/
            ├── entity/                   # 平铺：{Module}{Entity}.java
            ├── dto/                      # 平铺：{Module}{Entity}Dto.java
            └── controller/
                └── admin/                # 默认角色：admin
                    ├── product/          # 模块目录（从表名前缀提取）
                    │   └── InfoController.java
                    ├── order/
                    │   ├── InfoController.java
                    │   └── ItemController.java
                    └── guest/
                        └── UserController.java
```

### Controller 分包规则

**目录层级**：`controller/{role}/{module}/`

| 层级 | 来源 | 示例 |
|------|------|------|
| 角色 | 默认 `admin`，后续由 `220-admin-web-dev`/`220-guest-web-dev`/`220-admin-uni-dev`/`220-guest-uni-dev` 按需求移动 | `admin`、`saas`、`mch`、`ops` |
| 模块 | 代码生成器 zip 中已有的子目录 | `product/`、`order/`、`guest/` |
| 文件 | 代码生成器产出 | `InfoController.java` |

**代码生成器 zip 中的目录结构**：
```
controller/
├── product/
│   └── InfoController.java
├── order/
│   ├── InfoController.java
│   └── ItemController.java
└── guest/
    └── UserController.java
```

**脚本处理**：保留 zip 中的 module 子目录，注入 `admin` 角色层，替换包名为 `{项目包名}.controller.admin.{module}`。

## 下一步

代码生成完成后，提示用户进入 **`210-java-uniweb-dev`** 进行后端开发（TDD驱动）。

**流程位置**：`210-java-uniweb-init` → `210-java-uniweb-gencode` → **`210-java-uniweb-dev`**

## 参考

- [代码生成脚本](scripts/gencode.sh) - 支持 `--update` 增量更新模式
