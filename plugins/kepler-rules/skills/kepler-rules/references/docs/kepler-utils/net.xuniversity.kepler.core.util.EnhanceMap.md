# EnhanceMap<K, V>

增强版 Map，在标准 Map 基础上提供流式操作方法。

## 构造方法

### `EnhanceMap()`

默认构造，使用 HashMap 实现。

**示例：**
```java
EnhanceMap<String, Integer> map = new EnhanceMap<>();
map.put("age", 25);
```

### `EnhanceMap(Supplier<Map<K, V>> mapSupplier)`

使用指定的 Map 类型构造。

**参数：**
- `mapSupplier` - Map 供应器

**示例：**
```java
EnhanceMap<String, Integer> map = new EnhanceMap<>(LinkedHashMap::new);
```

### `EnhanceMap(Map<K, V> map)`

包装现有 Map。

**参数：**
- `map` - 已有的 Map 实例

**示例：**
```java
Map<String, Integer> original = new HashMap<>();
EnhanceMap<String, Integer> map = new EnhanceMap<>(original);
```

## 扩展方法

### `removeIf(Predicate<K> keyPredicate)`

根据条件移除元素。

**参数：**
- `keyPredicate` - Key 条件断言

**示例：**
```java
EnhanceMap<String, Integer> map = new EnhanceMap<>();
map.put("a", 1);
map.put("b", 2);
map.put("c", 3);
map.removeIf(key -> key.equals("a")); // 移除 key 为 "a" 的元素
```

### `filter(Predicate<? super K> keyFilter, Predicate<? super V> valueFilter)`

过滤元素，返回新 Map。

**参数：**
- `keyFilter` - Key 过滤条件
- `valueFilter` - Value 过滤条件

**返回：** 过滤后的新 EnhanceMap

**示例：**
```java
EnhanceMap<String, Integer> map = new EnhanceMap<>();
map.put("a", 1);
map.put("b", 2);
map.put("c", 3);

// 过滤 key 长度 > 0 且 value > 1 的元素
EnhanceMap<String, Integer> filtered = map.filter(k -> k.length() > 0, v -> v > 1);
// filtered 包含: {b=2, c=3}
```

### `map(Function<? super K, ? extends S> keyMapper, BiFunction<? super K, ? super V, ? extends R> valueMapper)`

转换 Key 和 Value，返回新 Map。

**参数：**
- `keyMapper` - Key 映射函数
- `valueMapper` - Value 映射函数

**返回：** 转换后的新 EnhanceMap

**示例：**
```java
EnhanceMap<String, Integer> map = new EnhanceMap<>();
map.put("a", 1);
map.put("b", 2);

// key 转大写，value 翻倍
EnhanceMap<String, Integer> mapped = map.map(
    String::toUpperCase,
    (k, v) -> v * 2
);
// mapped 包含: {A=2, B=4}
```

### `anyMatch(BiPredicate<? super K, ? super V> predicate)`

判断是否存在满足条件的元素。

**参数：**
- `predicate` - 条件断言

**返回：** `boolean` - 任一元素满足条件返回 true

**示例：**
```java
EnhanceMap<String, Integer> map = new EnhanceMap<>();
map.put("a", 1);
map.put("b", 2);

boolean result = map.anyMatch((k, v) -> v > 1); // true
```

### `allMatch(BiPredicate<? super K, ? super V> predicate)`

判断是否所有元素都满足条件。

**参数：**
- `predicate` - 条件断言

**返回：** `boolean` - 所有元素满足条件返回 true

**示例：**
```java
EnhanceMap<String, Integer> map = new EnhanceMap<>();
map.put("a", 1);
map.put("b", 2);

boolean result = map.allMatch((k, v) -> v > 0); // true
boolean result2 = map.allMatch((k, v) -> v > 1); // false
```

### `noneMatch(BiPredicate<? super K, ? super V> predicate)`

判断是否没有元素满足条件。

**参数：**
- `predicate` - 条件断言

**返回：** `boolean` - 没有元素满足条件返回 true

**示例：**
```java
EnhanceMap<String, Integer> map = new EnhanceMap<>();
map.put("a", 1);
map.put("b", 2);

boolean result = map.noneMatch((k, v) -> v > 10); // true
```
