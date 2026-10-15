---
name: "metax-op-develop"
description: "基于设计文档生成 Metax-TileLang 算子实现代码与测试。从 DESIGN.md 中提取关键信息，结合 tilelang-metax/examples/ 中的参考实现生成可运行代码。触发：实现算子、写 kernel、生成代码、算子编码。"
---

# Metax-TileLang 算子代码生成

基于设计文档（`DESIGN.md`）和已有示例，生成可运行的算子实现与测试。

---

## 1. 从 DESIGN.md 中提取的信息（只取这些）

| 提取字段 | 所在章节 | 用途 |
|---------|---------|------|
| 数学公式 | §1 概述 | 理解计算逻辑 |
| 算法步骤分解 | §1 算法描述 | 确定计算顺序 |
| API 映射表 | §3 API 映射设计 | **核心**：每步用哪个 TileLang API |
| 伪代码 | §3 计算伪代码 | **核心**：代码骨架 |
| 输入输出 shape 和 dtype | §4 数据规格 | 函数签名和测试数据 |
| block 大小 | §5 Tiling 策略 | 分块参数 |
| Golden 函数 | §9 验证方案 | 测试对比基准 |
| 测试用例表 | §9 L0 门槛测试计划 | 测试配置 |
| 精度标准 | §9 精度标准 | atol / rtol |

---

## 2. 参考来源（优先级高于 DESIGN.md 伪代码）

**当 DESIGN.md 伪代码与 `tilelang-metax/examples/` 中同类实现有冲突时，以 `tilelang-metax/examples/` 为准。**

### 2.1 API 用法

- 查阅 `metax-skills/metax-op-develop/references/` 中的参考文档
- TileLang 官方文档：`../tilelang-metax/tilelang/language/` 源码

### 2.2 同类算子示例

生成代码前，必须查阅 `tilelang-metax/examples/` 中的同类算子：

| 算子类型 | 参考示例 |
|---------|---------|
| 逐元素运算 | `tilelang-metax/examples/elementwise/` |
| 归约运算 | `tilelang-metax/examples/reduce/` |
| 归一化 | `tilelang-metax/examples/softmax/`、`tilelang-metax/examples/normalization/` |
| GEMM | `tilelang-metax/examples/gemm/` |
| 融合算子 | `tilelang-metax/examples/flash_attention/`、`tilelang-metax/examples/pipeline/` |

---

## 3. 代码生成流程

### 步骤 1：读取设计文档

读取 `DESIGN.md`，按 §1 表格提取字段。

### 步骤 2：查找参考示例

在 `tilelang-metax/examples/` 中找到最相似的算子实现，理解其结构和 API 用法。

### 步骤 3：编写 Kernel

```python
@tilelang.jit
def kernel(
    A: T.Buffer[S1, T.float16],
    B: T.Buffer[S2, T.float16],
    C: T.Buffer[S3, T.float16],
):
    # 1. 内存分配（自动 / 手动）
    # 2. 数据搬运 GM → Shared
    # 3. 计算逻辑
    # 4. 数据搬运 Shared → GM
```

### 步骤 4：编写 Golden 函数

使用 PyTorch 实现参考逻辑，作为精度对比基准。

### 步骤 5：编写测试用例

- L0：规则 shape（block 整除），快速精度收敛
- L1：不规则 shape / 尾块 shape
- L2：异常输入（空 tensor、极端 shape）
- Boundary：特殊值（INF / NAN / 极值）

### 步骤 6：运行与验证

```bash
# 确保 tilelang-metax 在 Python path 中
(cd ../tilelang-metax && pip install -e .) 2>/dev/null
# 运行 L0 测试
python custom/{op}/example_{op}.py --level l0
# 运行全量测试
python custom/{op}/example_{op}.py --level all
```

---

## 4. 输出契约

- `custom/{op}/example_{op}.py`：单一交付文件
  - `@tilelang.jit` kernel
  - 内嵌 PyTorch golden
  - 分层测试套件（L0/L1/L2/Boundary）
  - main 块支持 `--level` 参数
- golden 函数直接内嵌在同一文件中

---

## 5. 首跑前预检清单

- [ ] `example_{op}.py` 存在且完整
- [ ] `@tilelang.jit` 装饰器存在
- [ ] 内嵌 golden 函数存在
- [ ] main 块包含 `[PRECISION_PASS]` / `[PRECISION_FAIL]` 标记
- [ ] L0 用例与 DESIGN.md 计划一致
- [ ] `tilelang.disable_cache()` 调用存在
- [ ] main 块末尾含 `print("Test Passed!")` 或等价标记
