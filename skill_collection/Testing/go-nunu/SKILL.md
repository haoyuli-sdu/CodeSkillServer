---
name: "go-nunu"
description: "封装 go-nunu 官方文档为可被 Claude 直接调用的知识包。go-nunu 是基于 Golang 的应用脚手架（整合 Gin + GORM + Wire + Viper + Zap）。当用户在 Go 项目中使用 go-nunu 框架开发后端 API 服务时——包括创建项目、生成 handler/service/repository/model 组件、编写 Wire Provider 与编译依赖注入、配置 Viper / Zap、连接 MySQL（GORM）或 Redis、编写单元测试（gomock / sqlmock / redismock）、生成 Swagger 文档、使用热重载、了解分层架构与目录结构——必须使用本 Skill 来获取官方文档中的命令、API 签名与代码示例，避免凭记忆臆测 go-nunu 的命令名或参数。即使用户没有显式提到 \"go-nunu\"，只要在 Go 项目中提及 nunu、Wire、分层 handler/service/repository、nunu CLI 命令（如 nunu new / nunu create / nunu wire / nunu run），都应加载本 Skill。"
---

# go-nunu — Knowledge Skill

本 Skill 封装 [go-nunu](https://github.com/go-nunu/nunu) 官方文档为可被 Claude 直接调用的知识包。

go-nunu 是一个基于 Golang 的应用脚手架，整合了 Gin、GORM、Wire、Viper、Zap 等流行库，帮助你快速构建高效、可靠的应用程序。它采用经典的分层架构（handler → service → repository → model）并通过 Wire 预编译实现依赖注入。

## 为什么需要这个 Skill

go-nunu 项目的命脉是它自带的脚手架 CLI 与一套稳定的 API 签名。Claude 凭记忆写 go-nunu 代码时容易**臆造命令名**（如 `-template` 而非 `-r`）、**臆造 flag 参数**、**忘记 Wire 是预编译需重新 `nunu wire`**、**忘记面向接口编程是 mock 的前提**。本 Skill 把官方文档结构化封装到 `references/`，让 Claude 在生成代码时回到官方原文核对，从而减少踩坑。

## 如何使用本 Skill

按用户场景定位需要查阅的 reference 文件（位于本 Skill 的 `references/` 目录），**只读取对应 topic 的 reference 而非一次性加载全部**：

| 用户场景 | 优先查阅的 reference |
|---------|---------------------|
| 了解 go-nunu 的定位、功能特性、生态库列表、架构层级概览 | `references/overview.md` |
| 安装 Nunu CLI、配置 GOPROXY 加速、确认环境要求、验证安装 | `references/installation.md` |
| 使用 `nunu new` / `nunu create` / `nunu run` / `nunu wire` / `nunu upgrade` 等命令及其 flag 参数 | `references/cli-commands.md` |
| 选择项目模板（Basic / Advanced / Admin / MCP Server / Monorepo / Chat Layout） | `references/project-layouts.md` |
| 了解分层架构（cmd / config / internal / pkg）和各层职责、Wire 依赖注入机制 | `references/architecture.md` |
| 端到端开发流程：创建项目 → 创建组件 → 注册路由 → Wire → 配置 → 迁移 → 启动 | `references/project-workflow.md` |
| 配置 Viper 加载方式、Zap 日志配置项、代码中使用日志与配置注入 | `references/configuration.md` |
| 连接 MySQL（GORM）和 Redis、GORM model 定义、Repository 层面向接口编程 | `references/database.md` |
| 编写单元测试（gomock / sqlmock / redismock）、生成测试覆盖率报告 | `references/testing.md` |

## 给出建议时遵守的原则

reference 文件保留了官方文档的全部命令、API 签名和代码示例。生成代码时严格沿用这些 API 与示例——因为 go-nunu 的 CLI flag 名称、Wire provider 写法、GORM model 嵌入方式都是稳定约定，臆造会让用户跑到错误的命令或编译失败。能用 `nunu create` / `nunu new` / `nunu wire` 等脚手架命令生成的场景，优先使用 CLI 而非手写——这样既能避免命名/路径错位，又能保留 Wire 自动搜索 `wire.go` 的能力。

引用代码或命令时附加 reference 文件名（例如"见 `references/database.md` 的 `NewDB` 示例"），让用户能快速核实出处。

## 环境前提

- Go 1.19 或更高版本
- Git
- MySQL 5.7+（可选，使用数据库时）
- Redis（可选，使用缓存时）
- GOPROXY 国内加速：`https://goproxy.cn,direct`
