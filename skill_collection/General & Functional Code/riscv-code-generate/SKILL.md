---
name: "riscv-code-generate"
description: "RISC-V RTL 代码生成技能。当需要根据功能要求生成Scala/Chisel代码和build.sbt文件时使用此技能，这是RISC-V RTL自动化流水线的第3步。"
---

# RISC-V RTL 代码生成技能

此技能根据用户的功能要求生成 Scala/Chisel 代码和 build.sbt 文件，对应 CLAUDE.md 中自动化指令流水线的第3步。

## 技能功能

1. **Scala 代码生成** - 根据功能要求生成符合 RV32I 标准的 Chisel 代码
2. **创建 build.sbt** - 创建固定的构建配置文件

## 执行步骤

### 步骤3.1: Scala 代码生成

**开始执行第3.1步: Scala 代码生成**

根据用户提供的功能要求生成 Chisel 代码：

1. **获取功能需求**：
   - 从用户输入中提取硬件功能描述
   - 读取RV32I的指令规范并在后续编程中遵守，功能以用户输入的为准
   - 确定模块名称、接口信号和功能实现

2. **生成代码结构**：
   - 必须包含的头文件：
     ```scala
     import chisel3._
     import chisel3.util._
     import _root_.circt.stage.ChiselStage // 用于生成 Verilog
     ```
   - 模块类定义：`class <模块名> extends Module`
   - 端口定义：`val io = IO(new Bundle { ... })`
   - 功能实现逻辑

3. **添加生成器对象**（必须包含在结尾处）：
   ```scala
   // 定义 Main 对象以便手动调用生成器
   object <模块名>Gen extends App {
     ChiselStage.emitSystemVerilogFile(
       new <模块名>(),
       Array("--target-dir", "generated")
     )
   }
   ```
4. **检查规范**
   - 检查是否符合RV32I规范，可以忽略功能缺失的问题，若不符合修改代码
5. **保存文件**：
   - 保存到 `src/main/scala/<模块名>.scala`

**完成执行第3.1步: Scala 代码生成 - [成功/失败]**

### 步骤3.2: 创建 build.sbt

**开始执行第3.2步: 创建 build.sbt**

创建固定的 build.sbt 文件：

1. **文件内容**（必须使用如下版本，不得改变）：
   ```scala
   scalaVersion := "2.13.12"
   addCompilerPlugin("org.chipsalliance" % "chisel-plugin" % "6.0.0" cross CrossVersion.full)
   libraryDependencies += "org.chipsalliance" %% "chisel" % "6.0.0"
   scalacOptions ++= Seq("-feature", "-language:reflectiveCalls")
   ```

2. **保存文件**：
   - 保存到项目根目录的 `build.sbt` 文件

**完成执行第3.2步: 创建 build.sbt - [成功/失败]**

## 代码生成规范

### Chisel 代码模板

```scala
import chisel3._
import chisel3.util._
import _root_.circt.stage.ChiselStage // 用于生成 Verilog

class <模块名> extends Module {
  val io = IO(new Bundle {
    // 端口定义
    val in = Input(UInt(32.W))
    val out = Output(UInt(32.W))
    val enable = Input(Bool())
  })

  // 功能实现
  val reg = RegInit(0.U(32.W))
  when(io.enable) {
    reg := io.in
  }
  io.out := reg
}

// 定义 Main 对象以便手动调用生成器
object <模块名>Gen extends App {
  ChiselStage.emitSystemVerilogFile(
    new <模块名>(),
    Array("--target-dir", "generated")
  )
}
```


### 代码质量要求

1. **符合 RV32I 标准**
2. **模块化设计**：清晰的模块划分
3. **可读性**：适当的注释和命名
4. **可测试性**：便于编写 testbench

## 参考资料

- **ALU 实现模式**: `.claude/skills/riscv-code-generate/ALU_PATTERN.md`
- RV32I 规范: `references/rv32i-alu.md`


## 输出示例

```
开始执行第3.1步: Scala 代码生成
分析功能需求: 32位加法器模块
生成模块类: Adder
生成端口: a, b, sum
生成功能逻辑
保存文件: src/main/scala/Adder.scala
完成执行第3.1步: Scala 代码生成 - 成功

开始执行第3.2步: 创建 build.sbt
创建 build.sbt 文件
验证版本配置: scalaVersion 2.13.12, chisel 6.0.0
完成执行第3.2步: 创建 build.sbt - 成功
```

## 错误处理

如果代码生成失败，终止对话，输出：
```
完成执行第3.1步: Scala 代码生成 - 失败
原因: [具体原因，如功能需求不明确、模块名无效等]
```

如果 build.sbt 创建失败，终止对话，输出：
```
完成执行第3.2步: 创建 build.sbt - 失败
原因: [具体原因，如文件权限问题等]
```

## 注意事项

1. **代码头部必须包含**指定的 import 语句
2. **结尾必须包含**生成器对象
3. **【重要】禁止使用 `switch` + `VecInit` 索引方式** - firtool 会重排序操作
4. **【重要】必须使用 `MuxCase` 进行操作选择** - firtool 不会重排序
5. **ADD/SUB 使用 `sub_enable` 区分** - 4位操作码: `{sub_enable, funct3}`
6. **不需要实现的功能直接返回0即可**，使用 `MuxCase` 的默认值
7. **build.sbt 内容必须精确匹配**，不得修改版本号
8. 生成的代码应放在 `src/main/scala/` 目录下

## 相关技能

- `riscv-dir-init` - 目录初始化技能（上一步）
- `riscv-rtl-lint` - RTL构建和语法检查技能（下一步）
