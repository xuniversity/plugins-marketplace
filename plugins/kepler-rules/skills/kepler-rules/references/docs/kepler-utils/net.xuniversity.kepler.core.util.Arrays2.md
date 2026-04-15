# Arrays2

数组工具类，提供数组空值判断功能。

## 方法

### `notEmpty(Object[] array)`

判断数组是否非空。

**参数：**
- `array` - 数组

**返回：** `boolean` - 数组不为 null 且长度大于 0 返回 true

**示例：**
```java
String[] arr1 = {"a", "b"};
String[] arr2 = null;
String[] arr3 = {};

Arrays2.notEmpty(arr1); // true
Arrays2.notEmpty(arr2); // false
Arrays2.notEmpty(arr3); // false
```

### `isEmpty(Object[] array)`

判断数组是否为空。

**参数：**
- `array` - 数组

**返回：** `boolean` - 数组为 null 或长度为 0 返回 true

**示例：**
```java
String[] arr1 = {"a", "b"};
String[] arr2 = null;

Arrays2.isEmpty(arr1); // false
Arrays2.isEmpty(arr2); // true
```
