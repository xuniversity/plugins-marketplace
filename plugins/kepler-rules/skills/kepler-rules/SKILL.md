---
name: kepler-rules
description: 当用户发出“遵守编码规范”、“遵守rules”、“遵守项目已有编码规范”等类似指令时，使用这个技能。
---

# Kepler 项目编码规范技能

当用户要求遵守项目既有规范时，启用本技能并按本文件执行。

## 使用边界

1. 以项目既有规范为最高优先级，优先复用现有模式，不做风格漂移。
2. 如无必要，不新增工具类，不重复造轮子。
3. 只在任务涉及对应领域时应用该章节规则，避免无关约束污染实现。

## 高优先级禁止规则（P0，必须最先遵守）

1. 禁止在 Java 代码中使用类的全路径（FQCN）声明类型或调用方法；必须先通过 `import` 导入，再使用类短名。仅允许在 `import` 语句中出现全路径。
2. 禁止在 Service 层方法签名（入参/返回值）中使用 `Request`/`Response` 类；`Request` 到领域对象、领域对象到 `Response` 的转换统一在 Controller 层完成。

## 项目结构与技术栈

### 核心模块

- `kepler-parent`：父 POM，统一依赖与插件版本管理。
- `kepler-core`：核心工具类与基础组件。
- `kepler-support`：通用支持模块。
- `kepler-autoconfigure`：自动配置模块。

### 技术栈基线

- Java 21
- Spring Boot 3.5.3
- Spring Cloud 2025.0.0
- Spring Cloud Alibaba 2023.0.3.3
- Spring Security 6.5.0
- PostgreSQL / MySQL
- OpenFeign
- MyBatis

### 包结构与分层

- 统一包名前缀：`net.xuniversity.kepler`
- 常见目录分层：
  - `config/`
  - `controller/`
  - `service/`
  - `model/`
  - `util/`

### 异常处理

1. 如无必要，不在业务代码中显式 `try-catch`，交由全局异常处理器统一处理。
2. 业务异常优先使用 `net.xuniversity.kepler.core.KeplerException`。

### OpenFeign 约定

1. 微服务间调用优先使用 OpenFeign 接口声明。
2. 引入 openfeign 模块后，一般无需在业务模块重复声明 `@EnableFeignClients`。

### 数据可见范围过滤规范（VisibleClient）

1. 通过 `VisibleClient#getCurrentVisibility()` 进行数据权限过滤时，JPA 条件必须与 `kepler-base` 一致：
   - `allVisible == true`：不追加可见范围过滤条件。
   - `allVisible == false` 且 `workerIds` 为空：返回 `cb.disjunction()`（空结果）。
   - `allVisible == false` 且 `workerIds` 非空：追加 `IN (workerIds)` 过滤。
2. 禁止只判断 `workerIds` 是否为空而忽略 `allVisible`，否则会把全量权限误判为无权限。
3. `VisibleClient` 调用失败或 fallback 场景按 deny-all 处理：`allVisible=false`、`workerIds=emptySet`。
4. 推荐在 Service 内封装统一的可见范围 Predicate 构建逻辑，避免多处复制导致权限分支不一致。

## Java 编码规范

### 集合处理

1. 集合处理优先 `Stream API`。
2. 当 `stream()` 会显著降低可读性（如需额外 `final` 复制局部变量）时，可使用传统 `for` 循环。

### 注释原则

1. 注释应少而精，仅用于关键代码与隐含约束。
2. 避免逐行注释，优先让代码自解释。

### Lombok 与注入

1. 普通实体类优先使用 `@Data`。
2. Spring 托管类（如 `@Component`、`@Service`、`@Configuration`、`@Controller`）优先使用构造器注入，并通过 `@RequiredArgsConstructor` 配合 `final` 字段实现。
3. 避免字段注入 `@Autowired`。

### 命名规范

- 类名：`PascalCase`
- 方法名：`camelCase`
- 常量名：`UPPER_SNAKE_CASE`
- 包名：全小写

### Import 规范（高优先级）

1. 任何业务代码（字段、方法参数、返回值、泛型、方法体）都不得直接写类全路径，统一通过 `import` 后使用短类名。
2. 同名类冲突时，优先通过重命名模型（如 `TagEntity`/`TagResponse`）或拆分职责消除冲突，不以全路径作为规避手段。
3. 仅在两个类名称重复时在代码中使用全路径，且优先使用第三方框架的全路径。

## Spring Boot 最佳实践

### 配置与 Bean 管理

1. Spring Boot 应用优先使用 `@SpringBootConfiguration`；非 Boot 场景可使用 `@Configuration`。
2. 通过 `@EnableConfigurationProperties` 进行配置属性绑定。
3. 构造器注入优先，必要时使用 `@Lazy` 规避循环依赖。

### Spring Data

1. Repository 命名：
   - 返回集合：`findAllByXxx`
   - 返回单体：`findByXxx`
2. 查询策略优先级：
   - 方法名派生查询
   - `@Query` + JPQL
   - 最后才考虑原生 SQL
3. 避免 N+1 查询。
4. 查询默认不要将 `namespace` 作为筛选条件：
   - 大多数场景为单租户独立部署，库内天然是单租户数据。
   - 云端多租户场景由底层 `ProxySQL` 动态路由到目标租户库，不应在业务查询层重复追加 `namespace` 过滤。

### SpringDoc

1. Controller 与接口方法补充 SpringDoc 注解。
2. 文档描述保持简洁清晰。

### 接口设计

1. 遵循 RESTful，使用 HTTP 状态码表达结果。
2. Controller 返回 `ResponseEntity<T>`，不要直接返回实体对象。
3. `Request/Response` 对象需配套 JSR303 与 SpringDoc 注解。
4. Controller 负责 `Request/Response` 与领域模型之间的转换，Service 层禁止直接暴露 `Request/Response` 类型。

#### 多模块且包含 openfeign 模块

1. `Request/Response` 定义在 `kepler-{name}-openfeign` 模块。
2. `service` 模块提供显式转换器（如 `Function<Req, Entity>` / `Function<Entity, Resp>`）。

#### 非 openfeign 场景

1. `Request/Response` 可定义在服务模块。
2. `Response` 提供 `from(entity)` 工厂方法。
3. `Request` 提供 `toEntity()` 转换方法（实例方法或接收参数的静态方法）。

### HTTP 方法语义

1. `POST`：创建（`@Valid @RequestBody`）
2. `PATCH`：部分更新（通常 `@PathVariable + @RequestBody`）
3. `DELETE`：删除（通常配合路径参数）

### 数据库变更契约（Flyway，P0）

1. 生产库 Schema 变更必须通过 Flyway 版本脚本交付，禁止再以 `src/main/resources/database/schema.sql` 作为主迁移入口。
2. 迁移脚本目录统一为：`kepler-{module}-service/src/main/resources/database/migration/`。
3. 脚本命名统一为：`V{yyyy.MM.dd.NNN}__{description}.sql`（示例：`V2026.04.08.002__add_tag_table.sql`）。
4. 版本号必须严格递增，不允许插入历史版本；当 `out-of-order=false` 时，低版本补录会导致迁移失败。
5. 已发布版本脚本视为不可变更（immutable）；任何修复必须通过新增更高版本脚本完成，不得直接修改旧脚本。
6. 迁移脚本应优先使用幂等写法（如 `IF EXISTS` / `IF NOT EXISTS`），以提高跨环境重复执行安全性。
7. 若项目使用 PostgreSQL，`CREATE TABLE` 后必须补齐表与字段注释：
   - `COMMENT ON TABLE table_name IS '表中文语义';`
   - `COMMENT ON COLUMN table_name.column_name IS '字段中文语义';`
8. 审计字段统一语义：`created_by`（创建人）、`created_at`（创建时间）、`updated_by`（更新人）、`updated_at`（更新时间）。
9. 对保留字字段（如 `order`、`group`、`read`）在 DDL 与注释中统一使用双引号，保持 PostgreSQL 兼容性。
10. 测试目录下的 `src/test/resources/database/schema.sql` 仅用于测试初始化，不得作为生产库变更依据。

#### Flyway 基线对齐说明

1. 当前基线版本：`2026.04.08.000`。
2. 当前基线迁移脚本示例：`V2026.04.08.001__baseline_alignment.sql`。
3. 新增迁移脚本版本必须高于基线版本，且保持时间序与语义可追溯。

## 单元测试规范（新增）

### 测试类与包结构

1. 测试类命名统一为 `被测类名 + Test`（如 `TagServiceTest`、`TagControllerTest`）。
2. 测试包路径与生产代码保持镜像关系，便于定位和维护。

### 测试用例命名风格（参考 kepler-polaris）

1. 测试方法名使用英文 `lower_snake_case`，推荐模式：`should_{expected}_when_{condition}`。
2. 方法名必须同时表达“预期行为 + 触发条件”，禁止使用 `test1`、`shouldWork` 等弱语义命名。
3. 单个测试只验证一个核心行为，避免在一个方法中混合多个业务断言。

### 编写约定

1. 使用 Given-When-Then（或 Arrange-Act-Assert）组织测试步骤，确保结构清晰。
2. 断言优先使用 AssertJ（如 `assertThat`、`assertThatThrownBy`），异常分支必须断言异常类型与关键语义。
3. Service 层单测优先使用 `@ExtendWith(MockitoExtension.class)` + `@Mock` + `@InjectMocks`。
4. Controller 层测试优先使用 `@WebMvcTest` + `@AutoConfigureMockMvc(addFilters = false)` + `@MockitoBean`。
5. Converter 测试至少覆盖“全字段映射”和“可选字段为空”两类场景，保证转换稳定性。
6. 测试数据应固定且可读，避免引入随机值、当前时间等不稳定因素导致用例波动。

## Maven 配置规范

### 版本管理

1. 所有公共版本在 parent POM 的 `properties` 统一管理。
2. 依赖作用域规则：
   - 仅当前模块使用：在当前模块 `pom.xml` 添加。
   - 多模块共享：在 parent POM 管理。

### 关键版本基线

```xml
<properties>
    <java.version>21</java.version>
    <spring-cloud.version>2025.0.0</spring-cloud.version>
    <spring-cloud-alibaba.version>2023.0.3.3</spring-cloud-alibaba.version>
    <spring-security.version>6.5.0</spring-security.version>
</properties>
```

### 依赖与插件

1. 使用 BOM（如 `spring-cloud-dependencies`）进行版本对齐。
2. 关键插件：
   - `maven-compiler-plugin`
   - `maven-javadoc-plugin`
   - `maven-source-plugin`
   - `spring-boot-maven-plugin`
   - `com.diffplug.spotless:spotless-maven-plugin`
3. Java 编译目标与源码版本保持一致（`source/target = ${java.version}`）。

### 模块命名建议

- 父模块：`<packaging>pom</packaging>`
- 应用模块：`<packaging>jar</packaging>`
- 子模块建议：
  - `kepler-{model_name}-model`
  - `kepler-{model_name}-openfeign`
  - `kepler-{model_name}-service`

## 工具类使用规范（重点）

### 总原则

1. 如无必要，不创建新的工具类。
2. 先使用 `kepler-core` 提供的内置工具类。
3. 只有在内置工具类无法满足时，再评估项目已引入依赖中的工具能力。

### 登录态上下文获取

1. 获取当前登录用户信息时，统一使用 `net.xuniversity.kepler.support.spring.security.util.Contexts`。
2. 示例：使用 `Contexts.workerId()` 获取当前登录用户工号。

### 可用工具类

- `net.xuniversity.kepler.core.util.Arrays2`
- `net.xuniversity.kepler.core.util.Assert`
- `net.xuniversity.kepler.core.util.Collections3`
- `net.xuniversity.kepler.core.util.EnhanceMap`
- `net.xuniversity.kepler.core.util.Jacksons`
- `net.xuniversity.kepler.core.util.MapBuilder`
- `net.xuniversity.kepler.core.util.Maps2`
- `net.xuniversity.kepler.core.util.Strings2`

说明：
- `Jacksons` 仅在当前类不受 Spring 管理时用于 JSON 序列化/反序列化。
- Spring 托管类优先构造器注入 `ObjectMapper`，不要滥用 `Jacksons`。
- `MapBuilder` 用于构建可变 `Map`，语义类似 Guava `ImmutableMap` 的链式构建，但结果可变。

### 按需加载策略（必须遵守）

为控制上下文长度，禁止一次性读取全部工具类文档。仅在“确定要使用某个工具类”时读取对应文档。

文档目录（相对本技能目录）：
- `references/docs/kepler-utils`

按类名精确映射：

- `net.xuniversity.kepler.core.util.Arrays2`
  - `references/docs/kepler-utils/net.xuniversity.kepler.core.util.Arrays2.md`
- `net.xuniversity.kepler.core.util.Assert`
  - `references/docs/kepler-utils/net.xuniversity.kepler.core.util.Assert.md`
- `net.xuniversity.kepler.core.util.Collections3`
  - `references/docs/kepler-utils/net.xuniversity.kepler.core.util.Collections3.md`
- `net.xuniversity.kepler.core.util.EnhanceMap`
  - `references/docs/kepler-utils/net.xuniversity.kepler.core.util.EnhanceMap.md`
- `net.xuniversity.kepler.core.util.Jacksons`
  - `references/docs/kepler-utils/net.xuniversity.kepler.core.util.Jacksons.md`
- `net.xuniversity.kepler.core.util.MapBuilder`
  - `references/docs/kepler-utils/net.xuniversity.kepler.core.util.MapBuilder.md`
- `net.xuniversity.kepler.core.util.Maps2`
  - `references/docs/kepler-utils/net.xuniversity.kepler.core.util.Maps2.md`
- `net.xuniversity.kepler.core.util.Strings2`
  - `references/docs/kepler-utils/net.xuniversity.kepler.core.util.Strings2.md`

### 何时触发按需读取

1. 代码中出现目标工具类调用，且需要确认入参与边界行为。
2. 需要判断与 JDK / 三方库 API 的替换关系（例如是否应使用 `Collections3` 而非自写空值判断）。
3. 需要确保异常语义一致（例如 `Assert` 断言失败行为）。

## 执行清单

在产生代码前，按以下顺序进行自检：

1. 是否复用现有模块结构和命名规范。
2. 是否遵守 Java/Spring Boot/Maven 对应章节。
3. 是否避免重复造轮子，必要时按需读取工具类文档。
4. 是否避免引入计划外风格变更。

在输出说明中，如使用了工具类，需明确写出已读取的对应文档路径（仅列实际读取项）。
