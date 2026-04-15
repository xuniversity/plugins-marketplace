# Strings2

字符串工具类，提供字符串判断和替换功能。

## 常量

| 常量 | 值 |
|------|-----|
| `EMPTY` | `""` |
| `SPACE` | `" "` |
| `UNDERLINE` | `"_"` |
| `DOT` | `"."` |
| `COLON` | `":"` |
| `COMMA` | `","` |
| `SEMICOLON` | `";"` |
| `SLASH` | `"/"` |

## 方法

### `isBlank(CharSequence cs)`

判断字符串是否为空（包括 null、空字符串、纯空白字符）。

**参数：**
- `cs` - 字符序列

**返回：** `boolean` - 为空返回 true

**示例：**
```java
Strings2.isBlank(null);       // true
Strings2.isBlank("");         // true
Strings2.isBlank("   ");      // true
Strings2.isBlank("hello");    // false
Strings2.isBlank(" hello ");  // false
```

### `notBlank(CharSequence cs)`

判断字符串是否非空。

**参数：**
- `cs` - 字符序列

**返回：** `boolean` - 非空返回 true

**示例：**
```java
Strings2.notBlank("hello");   // true
Strings2.notBlank("");        // false
Strings2.notBlank(null);      // false
```

### `replace(String source, String target, String replacement)`

字符串替换。

**参数：**
- `source` - 源字符串
- `target` - 目标字符串（要替换的内容）
- `replacement` - 替换内容

**返回：** 替换后的字符串

**示例：**
```java
String result = Strings2.replace("hello world", "world", "java");
// 结果: "hello java"

String result2 = Strings2.replace("a-b-c", "-", "/");
// 结果: "a/b/c"
```
