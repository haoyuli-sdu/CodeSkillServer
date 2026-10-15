---
name: "test-unit"
description: "单元测试代码生成。当用户需要为代码生成单元测试、测试用例、Mock对象，或询问\"帮我写单元测试\"、\"生成测试代码\"时使用。"
---

# 单元测试代码生成

## 语言要求
**测试代码注释和测试描述必须使用中文**，包括 @DisplayName 测试名称、方法注释、场景说明等。

## 功能说明
生成高质量的单元测试代码，包括测试用例设计、Mock 对象、断言验证等。

## 文档依赖

生成单元测试时，可以参考以下文档：
- **设计文档**（可选）：参考 [/projectdocs/design/{name}_design.md](/projectdocs/design/)

## 使用方式

当用户提供待测代码（类/方法/模块），以及可选的设计文档路径或测试范围说明时，生成单元测试代码。

## 输入要求

**参考设计文档**（可选）：
- 如果有设计文档，可以参考 `design/gen` 命令生成的设计文档
- 设计文档位置：`/projectdocs/design/{project}_design_{timestamp}.md`
- 从设计文档中提取：
  - 接口定义和业务逻辑
  - 数据模型和字段验证规则
  - 异常场景和边界条件

**参考代码文件**：
- 可以直接为现有代码文件生成单元测试
- 支持为 Service、Controller、Mapper 等层生成测试

**分段生成策略**：
- 支持传入参数进行分段生成
- 用户可以指定生成测试的范围：
  - 按类生成：`unit --class=UserService` （只生成指定类的测试）
  - 按方法生成：`unit --method=createUser` （只生成指定方法的测试）
  - 按层生成：`unit --layer=service` （只生成指定层的测试）
  - 按模块生成：`unit --module=user` （生成指定模块的所有测试）
  - 按场景生成：`unit --scenario=normal,exception` （只生成指定场景的测试）

## 测试原则

### 1. FIRST 原则
- **F**ast（快速）：测试应该快速运行
- **I**ndependent（独立）：测试之间不应相互依赖
- **R**epeatable（可重复）：测试结果应该一致
- **S**elf-Validating（自我验证）：测试应该有明确的通过/失败结果
- **T**imely（及时）：测试应该及时编写

### 2. AAA 模式
- **Arrange**（准备）：设置测试数据和环境
- **Act**（执行）：执行被测试的方法
- **Assert**（断言）：验证结果是否符合预期

### 3. 测试覆盖原则
- 正常场景测试
- 边界条件测试
- 异常场景测试
- 并发场景测试（如需要）

## 测试生成步骤

### 1. 分析被测代码
- 理解方法功能和业务逻辑
- 识别输入参数和返回值
- 识别依赖的外部服务
- 识别可能的异常情况

### 2. 设计测试用例
- 列出所有测试场景
- 确定测试数据
- 设计 Mock 策略
- 确定断言内容

### 3. 生成测试代码
- 创建测试类
- 生成测试方法
- 添加 Mock 对象
- 编写断言语句
- 添加测试注释

### 4. 优化测试代码
- 提取公共测试数据
- 使用测试工具类
- 保持测试代码简洁
- 确保测试可读性

## 测试框架支持

### JUnit 5
```java
@Test
@DisplayName("测试描述")
void testMethod() {
    // Arrange
    // Act
    // Assert
}
```

### Mockito
```java
@Mock
private UserRepository userRepository;

@InjectMocks
private UserService userService;

@BeforeEach
void setUp() {
    MockitoAnnotations.openMocks(this);
}
```

### AssertJ
```java
assertThat(result)
    .isNotNull()
    .hasSize(3)
    .extracting(User::getName)
    .containsExactly("Alice", "Bob", "Charlie");
```

## 测试用例模板

### 基础测试模板
```java
@SpringBootTest
class UserServiceTest {
    
    @Mock
    private UserRepository userRepository;
    
    @InjectMocks
    private UserService userService;
    
    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }
    
    @Test
    @DisplayName("创建用户 - 成功场景")
    void testCreateUser_Success() {
        // Arrange
        UserDTO userDTO = new UserDTO();
        userDTO.setName("Alice");
        userDTO.setEmail("alice@example.com");
        
        User savedUser = new User();
        savedUser.setId(1L);
        savedUser.setName("Alice");
        
        when(userRepository.save(any(User.class)))
            .thenReturn(savedUser);
        
        // Act
        Long userId = userService.createUser(userDTO);
        
        // Assert
        assertThat(userId).isEqualTo(1L);
        verify(userRepository, times(1)).save(any(User.class));
    }
    
    @Test
    @DisplayName("创建用户 - 邮箱重复")
    void testCreateUser_EmailExists() {
        // Arrange
        UserDTO userDTO = new UserDTO();
        userDTO.setEmail("alice@example.com");
        
        when(userRepository.existsByEmail("alice@example.com"))
            .thenReturn(true);
        
        // Act & Assert
        assertThatThrownBy(() -> userService.createUser(userDTO))
            .isInstanceOf(BusinessException.class)
            .hasMessage("邮箱已存在");
        
        verify(userRepository, never()).save(any(User.class));
    }
    
    @Test
    @DisplayName("创建用户 - 参数为空")
    void testCreateUser_NullParameter() {
        // Act & Assert
        assertThatThrownBy(() -> userService.createUser(null))
            .isInstanceOf(IllegalArgumentException.class);
    }
}
```

## 测试场景覆盖

### 1. 正常场景
```java
@Test
@DisplayName("查询用户 - 用户存在")
void testGetUser_UserExists() {
    // 测试正常的业务流程
}
```

### 2. 边界条件
```java
@Test
@DisplayName("分页查询 - 页码为0")
void testPageQuery_PageNumZero() {
    // 测试边界值
}

@Test
@DisplayName("分页查询 - 每页大小为最大值")
void testPageQuery_MaxPageSize() {
    // 测试边界值
}
```

### 3. 异常场景
```java
@Test
@DisplayName("删除用户 - 用户不存在")
void testDeleteUser_UserNotFound() {
    // 测试异常情况
}

@Test
@DisplayName("更新用户 - 数据库异常")
void testUpdateUser_DatabaseException() {
    // 测试异常情况
}
```

### 4. 空值处理
```java
@Test
@DisplayName("创建用户 - 参数为null")
void testCreateUser_NullParameter() {
    // 测试空值处理
}

@Test
@DisplayName("查询用户 - 返回空列表")
void testQueryUsers_EmptyResult() {
    // 测试空结果
}
```

## Mock 策略

### 1. Mock 外部依赖
```java
// Mock Repository
@Mock
private UserRepository userRepository;

// Mock 外部服务
@Mock
private EmailService emailService;

// Mock Redis
@Mock
private RedisTemplate<String, Object> redisTemplate;
```

### 2. Mock 返回值
```java
// 返回特定值
when(userRepository.findById(1L))
    .thenReturn(Optional.of(user));

// 返回空值
when(userRepository.findById(999L))
    .thenReturn(Optional.empty());

// 抛出异常
when(userRepository.save(any()))
    .thenThrow(new DataAccessException("数据库异常"));
```

### 3. 验证调用
```java
// 验证方法被调用
verify(userRepository).save(any(User.class));

// 验证调用次数
verify(emailService, times(2)).sendEmail(anyString());

// 验证从未调用
verify(userRepository, never()).delete(any());

// 验证调用顺序
InOrder inOrder = inOrder(userRepository, emailService);
inOrder.verify(userRepository).save(any());
inOrder.verify(emailService).sendEmail(anyString());
```

## 断言技巧

### 基础断言
```java
// JUnit 断言
assertEquals(expected, actual);
assertTrue(condition);
assertNotNull(object);
assertThrows(Exception.class, () -> method());

// AssertJ 断言（推荐）
assertThat(actual).isEqualTo(expected);
assertThat(condition).isTrue();
assertThat(object).isNotNull();
assertThatThrownBy(() -> method())
    .isInstanceOf(Exception.class);
```

### 集合断言
```java
assertThat(list)
    .isNotEmpty()
    .hasSize(3)
    .contains("Alice", "Bob")
    .doesNotContain("Charlie");

assertThat(list)
    .extracting(User::getName)
    .containsExactly("Alice", "Bob", "Charlie");
```

### 对象断言
```java
assertThat(user)
    .isNotNull()
    .extracting(User::getName, User::getAge)
    .containsExactly("Alice", 25);

assertThat(user)
    .hasFieldOrPropertyWithValue("name", "Alice")
    .hasFieldOrPropertyWithValue("age", 25);
```

## 参数说明

### --class=<类名>
指定为某个类生成测试。

**示例**：
```bash
test/unit --class=UserService
test/unit --class=OrderController
test/unit --class=ProductMapper
```

### --method=<方法名>
指定只为某个方法生成测试（需要配合 --class 使用）。

**示例**：
```bash
test/unit --class=UserService --method=createUser
test/unit --class=UserService --method=updateUser,deleteUser
```

### --layer=<层级>
指定为某个层级的所有类生成测试。

**可用层级**：
- `service` - Service 层
- `controller` - Controller 层
- `mapper` - Mapper/DAO 层
- `util` - 工具类

**示例**：
```bash
test/unit --layer=service
test/unit --layer=controller
test/unit --layer=mapper
```

### --module=<模块名>
指定为某个模块的所有类生成测试。

**示例**：
```bash
test/unit --module=user
test/unit --module=order
test/unit --module=product
```

### --scenario=<场景列表>
指定只生成某些场景的测试用例，多个场景用逗号分隔。

**可用场景**：
- `normal` - 正常场景
- `exception` - 异常场景
- `boundary` - 边界条件
- `null` - 空值处理

**示例**：
```bash
test/unit --scenario=normal
test/unit --scenario=exception
test/unit --scenario=normal,exception
test/unit --scenario=normal,exception,boundary,null
```

### 组合使用
可以组合多个参数使用：

```bash
# 为指定模块的指定层生成测试
test/unit --module=user --layer=service

# 为指定类生成指定场景的测试
test/unit --class=UserService --scenario=exception

# 为指定模块的指定层生成指定场景的测试
test/unit --module=order --layer=service --scenario=normal,exception

# 为指定类的指定方法生成测试
test/unit --class=UserService --method=createUser,updateUser
```

## 最佳实践

### 1. 测试命名
```java
// 推荐：方法名_场景_预期结果
testCreateUser_EmailExists_ThrowsException()
testGetUser_UserNotFound_ReturnsNull()
testUpdateUser_ValidData_Success()

// 或使用 @DisplayName
@DisplayName("创建用户 - 邮箱已存在 - 抛出异常")
```

### 2. 测试隔离
```java
// 每个测试独立准备数据
@BeforeEach
void setUp() {
    // 准备测试数据
}

@AfterEach
void tearDown() {
    // 清理测试数据
}
```

### 3. 测试覆盖率
- 目标：代码覆盖率 > 80%
- 核心业务逻辑：100% 覆盖
- 工具类、常量类：可适当降低要求

### 4. 避免的做法
- ❌ 测试之间有依赖关系
- ❌ 测试访问真实数据库
- ❌ 测试依赖外部服务
- ❌ 测试包含 Thread.sleep()
- ❌ 过度使用 Mock

## 注意事项

1. **保持简单**：测试代码应该比被测代码更简单
2. **一个测试一个断言**：每个测试只验证一个场景
3. **测试可读性**：测试应该易于理解
4. **避免逻辑**：测试中不应该有复杂逻辑
5. **及时更新**：代码修改后同步更新测试
6. **分段生成**：对于大型项目，建议使用 `--module` 或 `--layer` 参数分段生成
7. **场景选择**：可以使用 `--scenario` 参数只生成特定场景的测试
