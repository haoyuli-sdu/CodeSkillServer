---
name: "app-to-cli"
description: "自动将桌面应用、Web应用、REST API服务快速转换为可交互式CLI命令行工具，支持自动生成命令解析、参数绑定、输入输出格式化、帮助文档。使用场景：(1) 用户需要为现有应用快速生成命令行界面 (2) 需要将API接口封装成CLI工具使用 (3) 提到\"把应用转成CLI\"、\"生成CLI工具\"、\"封装CLI\"、\"命令行包装\"等需求时触发。"
---

# App To Cli

## Overview

本技能可帮助你快速将任意应用、API服务封装为标准化的CLI工具，支持Python/Node.js/Go等多语言CLI生成，自动处理参数解析、帮助文档、输出格式化、错误处理等通用逻辑，无需手动编写重复的CLI模板代码。

## 核心功能

✨ **全自动化**: 一行命令完成所有流程，无需手动编写任何配置、无需执行多个步骤
1. **自动识别源类型**: 自动识别OpenAPI地址、本地可执行文件、配置文件，无需手动指定
2. **自动参数提取**: 对于本地应用自动解析`--help`输出提取参数，无需手动配置
3. **多语言支持**: 支持生成Python (Typer/Click)、Node.js (Commander)、Go (Cobra) 三种主流语言的CLI工具
4. **自动参数映射**: 自动识别API接口参数、应用输入参数，映射为CLI命令行参数/选项
5. **输出格式化**: 支持JSON/表格/纯文本三种输出格式，通过全局`--output`参数切换，自动处理分页、高亮
6. **帮助文档自动生成**: 自动生成命令帮助、参数说明、使用示例，内置`--help`、`--version`全局参数
7. **错误处理**: 内置异常捕获、友好错误提示、标准化退出码
8. **OpenAPI自动导入**: 只需提供OpenAPI/Swagger文档地址，自动生成完整配置文件，无需手动编写
9. **配置校验**: 自动校验配置文件合法性，提前发现配置错误
10. **自动安装依赖**: 生成CLI后自动安装所需依赖，开箱即用
11. **独立打包**: 一键将生成的CLI打包为独立EXE可执行文件，无需Python环境即可分发使用

## 使用流程

### 🚀 全自动化使用（推荐，只需一行命令）
不管是API还是本地应用，只需要运行一行命令即可生成完整可用的CLI：
```bash
python scripts/auto-generate.py <源地址/路径>
```

#### 示例：
1. **从OpenAPI生成CLI**：
```bash
python scripts/auto-generate.py https://api.example.com/v2/api-docs -o user-cli
```
2. **从本地EXE生成CLI**：
```bash
python scripts/auto-generate.py ./img-processor.exe -p
```
（-p 参数表示生成后自动打包为独立EXE）
3. **从配置文件生成CLI**：
```bash
python scripts/auto-generate.py ./my-config.yaml --no-install
```
（--no-install 表示不自动安装依赖）

---

### 手动控制流程（可选，需要自定义时使用）
#### 方式1：从OpenAPI生成
```bash
# 1. 导入OpenAPI生成配置
python scripts/openapi-import.py https://api.example.com/v2/api-docs -o config.yaml
# 2. （可选）调整配置文件
# 3. 生成CLI
python scripts/generate-cli.py config.yaml -o my-cli
```

#### 方式2：手动配置生成
```bash
# 1. 参考 references/example-config.yaml 编写配置文件
# 2. 校验配置
python scripts/validate-config.py config.yaml
# 3. 生成CLI
python scripts/generate-cli.py config.yaml -o my-cli
```

#### 打包为独立可执行文件
```bash
python scripts/package-executable.py ./my-cli
```

## 快速使用示例

### 示例1: 将REST API转换为CLI
输入：
> 帮我把https://api.example.com/users 这个用户管理API转成CLI，支持查询用户、创建用户、删除用户

输出：
自动生成`user-cli`工具，支持命令：
- `user-cli list [--page 1] [--size 10]` - 查询用户列表
- `user-cli get <user-id>` - 获取单个用户详情
- `user-cli create --name <name> --email <email>` - 创建用户
- `user-cli delete <user-id>` - 删除用户

### 示例2: 封装本地应用为CLI
输入：
> 我有一个图片处理工具app.exe，支持输入图片路径、输出格式、压缩率三个参数，帮我转成CLI

输出：
生成`img-cli`工具，支持命令：
- `img-cli process <input-path> --format <png/jpg/webp> --quality <0-100> [--output <output-path>]`

## 资源说明

### scripts/
- `generate-cli.py`: 核心生成脚本，传入配置文件即可生成完整CLI项目
- `validate-config.py`: 配置文件校验工具，检查输入的应用定义是否符合规范

### templates/
- `python-typer-template/`: Python Typer CLI项目模板
- `node-commander-template/`: Node.js Commander CLI项目模板
- `go-cobra-template/`: Go Cobra CLI项目模板

### references/
- `openapi-parser.md`: OpenAPI/Swagger文档解析指南
- `cli-design-best-practices.md`: CLI设计最佳实践规范
