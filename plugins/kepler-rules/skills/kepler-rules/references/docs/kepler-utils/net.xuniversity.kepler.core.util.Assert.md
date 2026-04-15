# Assert

断言工具类，用于参数校验。

## 方法

### `notNull(Object object, String message)`

断言对象不为 null，否则抛出 `IllegalArgumentException`。

**参数：**
- `object` - 待校验对象
- `message` - 异常信息

**异常：** `IllegalArgumentException` - 对象为 null 时抛出

**示例：**
```java
String name = null;
Assert.notNull(name, "name不能为空"); // 抛出 IllegalArgumentException: name不能为空

String value = "hello";
Assert.notNull(value, "value不能为空"); // 正常执行
```

### `isTrue(boolean expression, String message)`

断言表达式为 true，否则抛出 `IllegalArgumentException`。

**参数：**
- `expression` - 布尔表达式
- `message` - 异常信息

**异常：** `IllegalArgumentException` - 表达式为 false 时抛出

**示例：**
```java
int age = 15;
Assert.isTrue(age >= 18, "年龄必须满18岁"); // 抛出 IllegalArgumentException: 年龄必须满18岁

int adult = 20;
Assert.isTrue(adult >= 18, "年龄必须满18岁"); // 正常执行
```
