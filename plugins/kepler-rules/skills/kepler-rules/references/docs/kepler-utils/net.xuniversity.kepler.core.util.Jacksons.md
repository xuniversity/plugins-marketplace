# Jacksons

JSON 工具类，基于 Jackson ObjectMapper 封装。

## 工厂方法

### `newInstance()`

创建工具类实例。

**返回：** Jacksons 实例

**示例：**
```java
Jacksons jacksons = Jacksons.newInstance();
```

## 工厂方法（使用提供的ObjectMapper初始化工具类）

### `newInstance(ObjectMapper objectMapper)`

创建工具类实例。

**参数：**
- `objectMapper` - ObjectMapper 实例

**返回：** Jacksons 实例

**示例：**
```java
ObjectMapper mapper = new ObjectMapper();
Jacksons jacksons = Jacksons.newInstance(mapper);
```

## 方法

### `writeValueAsString(Object value)`

将对象序列化为 JSON 字符串。

**参数：**
- `value` - 待序列化对象

**返回：** `String` - JSON 字符串

**异常：** `RuntimeException` - 序列化失败时抛出

**示例：**
```java
ObjectMapper mapper = new ObjectMapper();
Jacksons jacksons = Jacksons.withObjectMapper(mapper);

User user = new User("张三", 25);
String json = jacksons.writeValueAsString(user);
// 结果: {"name":"张三","age":25}
```

### `readValue(String content, Class<T> valueType)`

将 JSON 字符串反序列化为对象。

**参数：**
- `content` - JSON 字符串
- `valueType` - 目标类型

**返回：** 反序列化后的对象

**异常：** `RuntimeException` - 反序列化失败时抛出

**示例：**
```java
String json = "{\"name\":\"张三\",\"age\":25}";
User user = jacksons.readValue(json, User.class);
```

### `readValue(String content, TypeReference<T> typeReference)`

将 JSON 字符串反序列化为带泛型的对象。

**参数：**
- `content` - JSON 字符串
- `typeReference` - 类型引用

**返回：** 反序列化后的对象

**异常：** `RuntimeException` - 反序列化失败时抛出

**示例：**
```java
String json = "[{\"name\":\"张三\",\"age\":25}]";
List<User> users = jacksons.readValue(json, new TypeReference<List<User>>() {});
```
