# Maps2

Map 工具类，提供 Map 空值判断功能。

## 方法

### `notEmpty(Map<?, ?> map)`

判断 Map 是否非空。

**参数：**
- `map` - Map 实例

**返回：** `boolean` - Map 不为 null 且非空返回 true

**示例：**
```java
Map<String, Integer> map1 = new HashMap<>();
map1.put("a", 1);

Map<String, Integer> map2 = null;
Map<String, Integer> map3 = new HashMap<>();

Maps2.notEmpty(map1); // true
Maps2.notEmpty(map2); // false
Maps2.notEmpty(map3); // false
```

### `isEmpty(Map<?, ?> map)`

判断 Map 是否为空。

**参数：**
- `map` - Map 实例

**返回：** `boolean` - Map 为 null 或空返回 true

**示例：**
```java
Map<String, Integer> map1 = new HashMap<>();
map1.put("a", 1);

Map<String, Integer> map2 = null;

Maps2.isEmpty(map1); // false
Maps2.isEmpty(map2); // true
```
