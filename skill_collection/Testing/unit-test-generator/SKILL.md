---
name: "unit-test-generator"
description: "为Java Spring Boot项目生成单元测试代码，使用JUnit 5 + Mockito + AssertJ，严格遵循 aIk-coding-style 规范。针对Service层和工具类生成测试，Mock外部依赖，聚焦核心业务逻辑验证。适用于需要快速建立单元测试覆盖的场景。"
---

# Unit Test Generator

> **重要**：本技能生成测试代码必须严格遵循 [aIk-coding-style](../aIk-coding-style/SKILL.md)（绝对路径：file:///c:/Users/arrowInknee/.lingma/skills/aIk-coding-style/SKILL.md） 规范。

## 核心规范引用

生成测试代码前必须阅读并遵循以下规范：

1. **类注释**：使用 `-anchor` 标记的固定格式，`@author a I k .`
2. **测试步骤注释**：使用 `-anchor` 标记（given/when/then）
3. **PO命名**：测试数据类使用 `XxPo` 命名规范

## Purpose

为Java Spring Boot项目生成高质量的单元测试代码，遵循JUnit 5 + Mockito + AssertJ技术栈，确保测试的可维护性和可读性。

## When to Use

- 为新开发的Service方法生成单元测试
- 为复杂业务逻辑方法补充测试
- 需要Mock外部依赖（Mapper、其他Service）进行隔离测试
- 验证条件分支、异常处理、边界值

## Testing Strategy

### 测试范围

**必须测试：**
- 复杂业务逻辑（订单状态流转、费用计算、审批流程）
- 条件分支超过2个的方法
- 涉及数学计算、日期处理、字符串处理的方法
- 自定义异常抛出和捕获逻辑

**不测试（避免过度测试）：**
- Lombok生成的getter/setter/equals/hashCode
- 简单的CRUD（无业务逻辑的save/getById）
- 配置类（@Configuration）
- @Valid注解的校验逻辑

### 测试结构

```java
/**
 * -anchor
 *
 * @author a I k .
 * @version 1.0.0
 * @implNote JDK 8
 * @apiNote
 * @since 2026/3/19 16:09
 * -
 **/
@ExtendWith(MockitoExtension.class)
@DisplayName("订单服务测试")
class OrderServiceTest {

    @Mock
    private OrderMapper orderMapper;

    @Mock
    private UserService userService;

    @InjectMocks
    private OrderServiceImpl orderService;

    @Nested
    @DisplayName("创建订单")
    class CreateOrderTest {

        @Test
        @DisplayName("正常创建订单成功")
        void createOrder_success() {
            // -anchor given
            // -anchor when
            // -anchor then
        }

        @Test
        @DisplayName("用户不存在时抛出异常")
        void createOrder_userNotFound_throwsException() {
            // -anchor given
            // -anchor when
            // -anchor then
        }
    }
}
```

**规范说明**：
- 测试类使用 `-anchor` 类注释
- 使用 `@DisplayName` 描述测试类和方法
- 测试步骤使用 `-anchor` 标记（given/when/then）

## 规范说明

- **所有测试代码必须严格遵循 [aIk-coding-style](../aIk-coding-style/SKILL.md)（绝对路径：file:///c:/Users/arrowInknee/.lingma/skills/aIk-coding-style/SKILL.md） 规范**
- **测试类使用 `-anchor` 类注释，`@author a I k .`**
- 使用 `@DisplayName` 描述测试类和方法
- **测试步骤使用 `-anchor` 标记（given/when/then）**
- **测试数据类使用 `XxPo` 命名规范**

## Generation Rules

### 1. 测试类命名

```java
// 被测类: OrderServiceImpl
// 测试类: OrderServiceTest 或 OrderServiceImplTest

// 被测类: StringUtil
// 测试类: StringUtilTest
```

### 2. 测试方法命名（中文DisplayName + 英文方法名）

```java
@Test
@DisplayName("正常创建订单成功")
void createOrder_success() { }

@Test
@DisplayName("用户不存在时抛出BusinessException")
void createOrder_userNotFound_throwsBusinessException() { }

@Test
@DisplayName("订单金额计算正确")
void calculateAmount_correct() { }
```

### 3. Given-When-Then 结构

```java
@Test
@DisplayName("根据ID查询订单成功")
void getById_success() {
    // given
    Long orderId = 1L;
    Order order = new Order();
    order.setId(orderId);
    order.setOrderNo("ORD202403180001");
    when(orderMapper.selectById(orderId)).thenReturn(order);

    // when
    Order result = orderService.getById(orderId);

    // then
    assertThat(result).isNotNull();
    assertThat(result.getOrderNo()).isEqualTo("ORD202403180001");
    verify(orderMapper).selectById(orderId);
}
```

### 4. Mock 规范

```java
// 正确：使用 when().thenReturn()
when(orderMapper.selectById(anyLong())).thenReturn(order);

// 正确：使用 doReturn().when() 避免真实方法调用
doReturn(order).when(orderMapper).selectById(anyLong());

// 正确：验证方法被调用
createOrderMapper.insert(any(Order.class));

// 正确：验证调用次数
verify(orderMapper, times(1)).selectById(anyLong());
verify(orderMapper, never()).updateById(any());

// 正确：参数匹配器
when(orderMapper.selectById(eq(1L))).thenReturn(order);
when(orderMapper.selectList(any(LambdaQueryWrapper.class))).thenReturn(list);
```

### 5. AssertJ 断言风格

```java
// 对象断言
assertThat(result).isNotNull();
assertThat(result.getId()).isEqualTo(1L);
assertThat(result.getStatus()).isIn(0, 1, 2);

// 集合断言
assertThat(orderList).hasSize(3);
assertThat(orderList).extracting(Order::getStatus).containsOnly(1);
assertThat(orderList).isEmpty();

// 异常断言
assertThatThrownBy(() -> orderService.createOrder(null))
    .isInstanceOf(BusinessException.class)
    .hasMessageContaining("订单信息不能为空");

// 布尔断言
assertThat(result.isPaid()).isTrue();
assertThat(orderList.isEmpty()).isFalse();
```

### 6. 静态常量提取

```java
/**
 * -anchor
 *
 * @author a I k .
 * @version 1.0.0
 * @implNote JDK 8
 * @apiNote
 * @since {yyyy/MM/dd}
 * -
 **/
@ExtendWith(MockitoExtension.class)
@DisplayName("订单服务测试")
class OrderServiceTest {

    private static final Long TEST_ORDER_ID = 1L;
    private static final String TEST_ORDER_NO = "ORD202403180001";
    private static final Long TEST_USER_ID = 100L;

    // ...
}
```

## Java 8 Compliance

```java
// 正确：使用Arrays.asList
List<Order> orders = Arrays.asList(order1, order2);

// 正确：使用Stream API
List<Long> ids = orders.stream()
    .map(Order::getId)
    .collect(Collectors.toList());

// 正确：使用Optional
Optional.ofNullable(order).ifPresent(o -> {
    assertThat(o.getStatus()).isEqualTo(1);
});

// 错误：使用List.of（Java 9+）
List<Order> orders = List.of(order1, order2); // 禁止
```

## Dependencies

```xml
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-junit-jupiter</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.assertj</groupId>
    <artifactId>assertj-core</artifactId>
    <scope>test</scope>
</dependency>
```

## Output Location

```
src/test/java/com/example/module/service/OrderServiceTest.java
```

## Example Output

```java
package com.example.order.service;

import com.example.order.entity.OrderPo;
import com.example.order.mapper.OrderMapper;
import com.example.user.service.UserService;
import com.example.common.exception.BusinessException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.*;

/**
 * -anchor
 *
 * @author a I k .
 * @version 1.0.0
 * @implNote JDK 8
 * @apiNote
 * @since 2026/3/19 16:09
 * -
 **/
@ExtendWith(MockitoExtension.class)
@DisplayName("订单服务测试")
class OrderServiceTest {

    @Mock
    private OrderMapper orderMapper;

    @Mock
    private UserService userService;

    @InjectMocks
    private OrderServiceImpl orderService;

    private static final Long TEST_ORDER_ID = 1L;
    private static final Long TEST_USER_ID = 100L;

    @Nested
    @DisplayName("创建订单")
    class CreateOrderTest {

        @Test
        @DisplayName("正常创建订单成功")
        void createOrder_success() {
            // -anchor given
            OrderPo order = new OrderPo();
            order.setUserId(TEST_USER_ID);
            order.setAmount(new BigDecimal("100.00"));

            when(userService.existsById(TEST_USER_ID)).thenReturn(true);
            when(orderMapper.insert(any(OrderPo.class))).thenAnswer(invocation -> {
                OrderPo o = invocation.getArgument(0);
                o.setId(TEST_ORDER_ID);
                return 1;
            });

            // -anchor when
            Long result = orderService.createOrder(order);

            // -anchor then
            assertThat(result).isEqualTo(TEST_ORDER_ID);
            verify(userService).existsById(TEST_USER_ID);
            verify(orderMapper).insert(any(OrderPo.class));
        }

        @Test
        @DisplayName("用户不存在时抛出异常")
        void createOrder_userNotFound_throwsException() {
            // -anchor given
            OrderPo order = new OrderPo();
            order.setUserId(TEST_USER_ID);

            when(userService.existsById(TEST_USER_ID)).thenReturn(false);

            // -anchor when & then
            assertThatThrownBy(() -> orderService.createOrder(order))
                .isInstanceOf(BusinessException.class)
                .hasMessageContaining("用户不存在");

            verify(orderMapper, never()).insert(any());
        }
    }

    @Nested
    @DisplayName("查询订单")
    class QueryOrderTest {

        @Test
        @DisplayName("根据ID查询订单成功")
        void getById_success() {
            // -anchor given
            OrderPo order = new OrderPo();
            order.setId(TEST_ORDER_ID);
            order.setOrderNo("ORD202403180001");

            when(orderMapper.selectById(TEST_ORDER_ID)).thenReturn(order);

            // -anchor when
            OrderPo result = orderService.getById(TEST_ORDER_ID);

            // -anchor then
            assertThat(result).isNotNull();
            assertThat(result.getOrderNo()).isEqualTo("ORD202403180001");
        }

        @Test
        @DisplayName("订单不存在时返回null")
        void getById_notFound_returnsNull() {
            // -anchor given
            when(orderMapper.selectById(TEST_ORDER_ID)).thenReturn(null);

            // -anchor when
            OrderPo result = orderService.getById(TEST_ORDER_ID);

            // -anchor then
            assertThat(result).isNull();
        }
    }
}
```

**规范说明**：
- **测试类使用 `-anchor` 类注释，`@author a I k .`**
- 使用 `@DisplayName` 描述测试类和方法
- **测试步骤使用 `-anchor` 标记（given/when/then）**
- **测试数据类使用 `XxPo` 命名规范**
- **PO对象构造**：根据 PO 类型选择构造方式
  - 无继承 PO：使用 `new XxPo()` + setter 或 `XxPo.builder()`
  - 有继承 PO：使用 `new XxPo()` + setter（需要显式无参构造）

---

## Controller 测试

使用 `@WebMvcTest` 进行 Controller 层切片测试：

```java
/**
 * -anchor
 *
 * @author a I k .
 * @version 1.0.0
 * @implNote JDK 8
 * @apiNote
 * @since 2026/3/19 16:09
 * -
 **/
@WebMvcTest(OrderController.class)
@DisplayName("订单控制器测试")
class OrderControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private OrderService orderService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("创建订单接口_成功")
    void shouldCreateOrderSuccess() throws Exception {
        // -anchor Given
        OrderCreateDto dto = new OrderCreateDto();
        OrderVo vo = OrderVo.builder().id(1L).orderNo("202403180001").build();
        when(orderService.createOrder(any())).thenReturn(vo);

        // -anchor When & Then
        mockMvc.perform(post("/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(dto)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.orderNo").value("202403180001"));
    }
}
```

## Mapper 测试

使用 `@MybatisPlusTest` 进行数据访问层测试：

```java
@MybatisPlusTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@DisplayName("订单Mapper测试")
class OrderMapperTest {

    @Autowired
    private OrderMapper orderMapper;

    @Test
    @DisplayName("插入订单")
    void shouldInsertOrder() {
        OrderPo order = OrderPo.builder()
                .orderNo("202403180001").userId(1L).status(0).build();
        int result = orderMapper.insert(order);
        assertThat(result).isEqualTo(1);
        assertThat(order.getId()).isNotNull();
    }
}
```

## 测试数据准备

使用 `@BeforeAll` / `@BeforeEach` 准备通用测试数据：

```java
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class OrderServiceTest {

    private OrderCreateDto validOrderDto;

    @BeforeAll
    void setUp() {
        validOrderDto = OrderCreateDto.builder()
                .userId(1L).addressId(1L).build();
    }
}
```

## 测试覆盖场景

| 场景 | 说明 | 示例 |
|------|------|------|
| **正常流程** | 标准业务流程 | 创建订单成功 |
| **异常流程** | 业务异常 | 库存不足 |
| **边界条件** | 极限值 | 最大数量、空列表 |
| **空值处理** | null 处理 | 参数为 null |
| **并发场景** | 多线程 | 库存扣减 |

## Output Location

```
src/test/java/com/example/module/
├── service/
│   └── OrderServiceTest.java
├── controller/
│   └── OrderControllerTest.java
└── mapper/
    └── OrderMapperTest.java
```

## 注意事项

- 单元测试要独立，不依赖外部服务
- 使用 Mockito 模拟依赖
- 测试数据使用 Builder 模式构建
- 测试方法名要清晰描述测试场景
- 正常、异常、边界场景都要覆盖
- 数据库测试使用 @MybatisPlusTest
- Controller 测试使用 @WebMvcTest
- 简单数据处理使用 Stream API，复杂逻辑使用传统循环
