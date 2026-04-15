# Collections3

集合工具类，提供集合空值判断功能。

## 方法

### `isEmpty(Collection<?> coll)`

判断集合是否为空。

**参数：**
- `coll` - 集合

**返回：** `boolean` - 集合为 null 或空集合返回 true

**示例：**
```java
List<String> list1 = Arrays.asList("a", "b");
List<String> list2 = null;
List<String> list3 = new ArrayList<>();

Collections3.isEmpty(list1); // false
Collections3.isEmpty(list2); // true
Collections3.isEmpty(list3); // true
```

### `notEmpty(Collection<?> coll)`

判断集合是否不为空。

**参数：**
- `coll` - 集合

**返回：** `boolean` - 集合不为 null 且非空返回 true

**示例：**
```java
List<String> list1 = Arrays.asList("a", "b");
List<String> list2 = null;

Collections3.notEmpty(list1); // true
Collections3.notEmpty(list2); // false
```
