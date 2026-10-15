---
name: "go-cli"
description: "交互式生成一套遵循「按业务能力分包」最佳实践的 Go 项目架构（gin + gorm）。以询问的形式让用户多选数据库（MySQL/PostgreSQL/SQLite/SQL Server/TiDB/OceanBase/ClickHouse），并询问是否开启 Swagger，然后落地生成完整可编译的项目骨架。Use when the user wants to bootstrap/scaffold a new Go backend project, create a Go project structure with gin and gorm, or asks 搭建 Go 项目/项目架构/脚手架."
---

# go-cli

## Overview

根据《告别 pkg 和 util 滥用：Go 项目结构的最佳实践》的理念，交互式生成一个基于
**gin + gorm** 的 Go 后端项目骨架，并落地为可直接 `go build` 的完整工程。适用于任意新建 Go 后端项目。

核心设计原则：

- **按业务能力分包**，而不是按技术层（controller/service/dao）分顶层目录。
- 顶层业务域用**领域名词**：`internal/user`、`internal/order`……域内再按 `handler.go / service.go / repo.go / model.go` 分文件。
- 共用能力放在**语义明确的名词包** `internal/platform/*`（config、logger、database、httpserver），**禁止 util / common / helper 黑洞包**。
- `internal/` 放应用私有代码，`pkg/` 只放真正要对外复用的公共库（默认不生成 pkg）。

**交付形态**：本 skill 携带一个零依赖的 Python 生成器 `scripts/scaffold.py`，内嵌全部 Go 模板。
你（AI）的职责是**驱动交互、组装参数、调用脚本**，而不是手写整套项目代码。

## Prerequisites

- 本机需有 **Python 3.8+**（运行生成器；Windows 上 `python` 不可用时用 `py`）。
- 生成后编译需 **Go 1.22+**。
- 生成器只写文件，不联网、不执行 `go` 命令；依赖拉取与编译交给用户确认后进行。

> 生成器路径以本 skill 的 base directory 为准，即 `<SKILL_DIR>/scripts/scaffold.py`。

## Workflow

### Step 1 — 收集基本信息

用 `ask_followup_question` 询问（能从上下文推断则直接推断，减少打断）：

- **项目模块名 module**：go.mod 的 module path，如 `github.com/foo/bar` 或 `myapp`。
- **目标目录**：默认当前工作目录下以 module 末段命名的文件夹。

### Step 2 — 询问数据库（多选，必须以询问形式）

必须用 `ask_followup_question` 且 `multiSelect: true` 让用户多选，选项固定为以下 7 项：

- `MySQL`
- `PostgreSQL`
- `SQLite`
- `SQL Server`
- `TiDB`（走 MySQL 驱动，兼容 MySQL 协议）
- `OceanBase`（走 MySQL 驱动，兼容 MySQL 协议）
- `ClickHouse`（GORM 社区驱动）

允许一个都不选（生成不含 DB 装配的纯 gin 骨架，user 用内存仓储）。至少选一个时，生成器会：

- 装配对应 GORM 驱动依赖；
- 在 `internal/platform/database` 生成多驱动 `Open()` 工厂（按 `driver` 配置项 switch）；
- 在 `configs/config.yaml` 写入每种所选数据库的示例 DSN 配置。

### Step 3 — 询问是否开启 Swagger（必须以询问形式）

用 `ask_followup_question` 询问「是否开启 Swagger」（是/否）。选“是”则：

- 依赖加入 `swaggo/gin-swagger`、`swaggo/files`、`swaggo/swag`；
- `main.go` 挂载 `/swagger/*any` 路由与通用 API 注解；
- handler 上生成 swag 注解示例；
- 生成 `docs/` 占位说明（提示用户运行 `swag init` 生成真实文档）。

### Step 4 — 调用生成器落地

把上述选择组装成命令行参数调用脚本：

```bash
python "<SKILL_DIR>/scripts/scaffold.py" \
  --module <module> \
  --output <target_dir> \
  --databases mysql,postgres,sqlite,sqlserver,tidb,oceanbase,clickhouse \
  --swagger yes
```

参数说明：

- `--databases`：逗号分隔，取值集合 `mysql,postgres,sqlite,sqlserver,tidb,oceanbase,clickhouse`；不选传空或省略。
- `--swagger`：`yes` / `no`。
- `--force`：目标目录非空时覆盖（谨慎，先询问用户）。

### Step 5 — 生成后收尾（告知用户，不要自动执行网络下载类命令）

- 提示用户在项目目录执行：`go mod tidy` 拉取依赖、`go build ./...` 验证编译。
- 若开启 Swagger，提示执行：`go install github.com/swaggo/swag/cmd/swag@latest && swag init -g cmd/api/main.go -o docs`。

### Step 6 — 根据实际生成的结构讲解（必做）

生成完成后，**必须先读取本次真实落地的目录**（用 list_dir / 读取关键文件确认，而不是照搬预览模板），
再据此向用户讲解。因为最终结构会随「所选数据库」「是否开启 Swagger」而不同（例如未选数据库时
没有 `internal/platform/database/` 且 user 用内存仓储；未开 Swagger 时没有 `docs/`）。

讲解需覆盖以下几点，做到「对着当前这套代码讲」：

1. **整体分层概览**：用一棵目录树列出本次**实际生成**的文件（体现有/无 `database`、有/无 `docs` 的差异），
   并点明这套结构遵循「按业务能力分包」——业务域在 `internal/<domain>/`，基础设施在 `internal/platform/*`，无 util 黑洞。
2. **入口与装配**：`cmd/api/main.go` 如何加载配置 → 建日志 →（若有 DB）打开数据库并 AutoMigrate → 组装 user 域 → 注册路由 → 启动。
3. **业务域 user 的四件套**：`model.go / repo.go / service.go / handler.go` 各自职责与调用链（handler→service→repo）。
4. **platform 各基础设施包**：逐个说明本次生成了哪些（`config` / `logger` / `httpserver`／按需 `database`）及其作用；
   若含 `database`，说明它是多驱动工厂，本次装配了哪些数据库、如何按 `config.yaml` 的 `driver` 切库。
5. **配置文件**：`configs/config.yaml` 的关键项（server / log ／按需 database.dsn 列表与 pool）。
6. **Swagger（若开启）**：`/swagger/*any` 路由、handler 上的注解、如何 `swag init` 生成文档。
7. **如何扩展**：新增业务域 = 新建 `internal/<domain>/` 放 `handler/service/repo/model.go` 并在 main.go 装配注册；
   强调**不要**新建 util/common/helper 包。

讲解风格：简洁、结构化（可用小标题或列表），突出「为什么这么分」，避免逐行贴代码。

## 生成结果结构预览

```
<project>/
├── cmd/
│   └── api/
│       └── main.go              # 组装依赖、启动 gin
├── internal/
│   ├── user/                    # 业务域示例（按业务能力分包）
│   │   ├── handler.go
│   │   ├── service.go
│   │   ├── repo.go
│   │   └── model.go
│   └── platform/                # 基础设施（语义明确的名词包，非 util）
│       ├── config/
│       ├── logger/
│       ├── database/            # 多驱动 GORM 工厂（按所选数据库装配）
│       └── httpserver/
├── configs/
│   └── config.yaml
├── docs/                        # 仅在开启 Swagger 时生成
├── go.mod
├── .gitignore
└── README.md
```

## Notes

- **一律用脚本生成**：不要手写整套项目，全部通过 `scripts/scaffold.py` 落地，保证可复现。
- **两个决策必须询问**：数据库（多选）与是否开启 Swagger 必须**以询问的形式**让用户决定。
- **生成后必讲解**：生成完成后要对着本次**真实落地**的结构讲解（见 Workflow Step 6），而非照搬「生成结果结构预览」——预览是最全形态，实际会因数据库/Swagger 选择而增减 `database`、`docs` 等。
- **开箱即编译**：go.mod 模板已内置 `github.com/ugorji/go/codec v1.2.12` 约束，规避 gin v1.10 的 ambiguous import；生成后 `go mod tidy && go build ./...` 直接通过。
- **自动格式化**：若本机有 `gofmt`，生成器会自动格式化产物（import 分组/排序）。
- **无数据库场景**：不选数据库时，user 域使用内存仓储实现（`sync.RWMutex + map`），同样可编译运行。
- **扩展业务域**：想加 `order` 域，只需新建 `internal/order/` 放入 `handler/service/repo/model.go`，在 `cmd/api/main.go` 装配并注册路由；**不要**新建 util/common 包。
