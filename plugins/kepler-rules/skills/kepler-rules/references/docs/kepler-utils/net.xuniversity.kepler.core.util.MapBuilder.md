# MapBuilder<K, V>

Map 构建器，使用建造者模式构建可变 Map。

## 工厂方法

### `newInstance()`

创建默认构建器，使用 HashMap 实现。

**返回：** MapBuilder 实例

**示例：**
```java
Map<String, Integer> map = MapBuilder.<String, Integer>newInstance()
    .put("a", 1)
    .put("b", 2)
    .build();
```

### `newInstance(Map<K, V> map)`

基于现有 Map 创建构建器。

**参数：**
- `map` - 已有的 Map 实例

**返回：** MapBuilder 实例

**示例：**
```java
Map<String, Integer> base = new HashMap<>();
Map<String, Integer> map = MapBuilder.newInstance(base)
    .put("a", 1)
    .build();
```

### `newInstance(Supplier<Map<K, V>> supplier)`

使用供应器创建指定类型的构建器。

**参数：**
- `supplier` - Map 供应器

**返回：** MapBuilder 实例

**示例：**
```java
Map<String, Integer> map = MapBuilder.<String, Integer>newInstance(LinkedHashMap::new)
    .put("a", 1)
    .put("b", 2)
    .build();
```

## 方法

### `put(K key, V value)`

添加元素。

**参数：**
- `key` - 键
- `value` - 值

**返回：** 当前 MapBuilder 实例（链式调用）

**示例：**
```java
Map<String, Integer> map = MapBuilder.<String, Integer>newInstance()
    .put("name", "张三")
    .put("age", 25)
    .build();
```

### `putIf(K key, V value, Predicate<K> predicate)`

满足 Key 条件时添加元素。

**参数：**
- `key` - 键
- `value` - 值
- `predicate` - Key 条件断言

**返回：** 当前 MapBuilder 实例（链式调用）

**示例：**
```java
Map<String, Integer> map = MapBuilder.<String, Integer>newInstance()
    .putIf("a", 1, key -> key.length() > 0)  // 满足条件，添加
    .putIf("", 2, key -> key.length() > 0)    // 不满足条件，不添加
    .build();
// 结果: {a=1}
```

### `putIf(K key, V value, BiPredicate<K, V> predicate)`

满足 Key-Value 条件时添加元素。

**参数：**
- `key` - 键
- `value` - 值
- `predicate` - Key-Value 条件断言

**返回：** 当前 MapBuilder 实例（链式调用）

**示例：**
```java
Map<String, Integer> map = MapBuilder.<String, Integer>newInstance()
    .putIf("a", 1, (k, v) -> v > 0)   // 满足条件，添加
    .putIf("b", -1, (k, v) -> v > 0)  // 不满足条件，不添加
    .build();
// 结果: {a=1}
```

### `putAll(Map<K, V> map)`

批量添加元素。

**参数：**
- `map` - 待添加的 Map

**返回：** 当前 MapBuilder 实例（链式调用）

**示例：**
```java
Map<String, Integer> base = new HashMap<>();
base.put("x", 10);
base.put("y", 20);

Map<String, Integer> map = MapBuilder.<String, Integer>newInstance()
    .put("a", 1)
    .putAll(base)
    .build();
// 结果: {a=1, x=10, y=20}
```

### `build()`

构建 Map。

**返回：** 构建好的 Map 实例
