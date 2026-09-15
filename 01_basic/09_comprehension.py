"""
推导式 —— Python 最优雅的特性之一

【推导式是什么?】

  推导式是把"循环 + 条件 + 变换"浓缩到一行表达式的写法.
  它让代码更短, 更易读, 通常也更快 (C 层面优化).

  Python 支持三种推导式:
    [x for x in seq]       列表推导式
    {k: v for k, v in seq}  字典推导式
    {x for x in seq}        集合推导式

  第四种不是推导式但很像:
    (x for x in seq)        生成器表达式 (惰性, 不马上创建)

【推导式 vs for 循环的速度对比】

  推导式在 CPython 中比等价的 for 循环快, 因为:
    1. 循环逻辑在 C 层面执行
    2. .append() 方法调用被优化为直接 C 函数调用

  但这不意味着应该把所有 for 循环都改成推导式.
  如果逻辑复杂 (多行, 嵌套太深), for 循环更可读.

【什么时候不要用推导式?】

  1. 逻辑超过 2 行 → 用 for 循环
  2. 嵌套超过 2 层 → 用 for 循环
  3. 需要副作用 (如写入文件, 修改外部变量) → 用 for 循环
  4. 异常处理 → 用 for 循环
"""

# ============================================================
# 1. 列表推导式
# ============================================================
print("--- 列表推导式 ---")

# 基础: 对每个元素做变换
squares = [x**2 for x in range(5)]
print(f"  平方: {squares}")           # [0, 1, 4, 9, 16]

# 带条件过滤
evens = [x for x in range(10) if x % 2 == 0]
print(f"  偶数: {evens}")

# 带条件变换 (if-else 在左边)
labels = ["even" if x % 2 == 0 else "odd" for x in range(4)]
print(f"  标签: {labels}")

# 等价 for 循环对比
result = []
for x in range(10):
    if x % 2 == 0:
        result.append(x)

result2 = [x for x in range(10) if x % 2 == 0]
assert result == result2
print(f"  等价性验证: {result == result2}")

# ============================================================
# 2. 字典推导式
# ============================================================
print("\n--- 字典推导式 ---")

# key: value 对
square_map = {x: x**2 for x in range(5)}
print(f"  x → x^2: {square_map}")

# 从已有字典过滤
d = {"a": 1, "b": 2, "c": 3}
filtered = {k: v for k, v in d.items() if v > 1}
print(f"  过滤 value > 1: {filtered}")

# ============================================================
# 3. 集合推导式
# ============================================================
print("\n--- 集合推导式 ---")

# 自动去重
words = ["hello", "world", "hello"]
unique_lengths = {len(w) for w in words}
print(f"  单词长度 (去重): {unique_lengths}")   # {5}

# ============================================================
# 4. 生成器表达式 (不是推导式!)
# ============================================================
print("\n--- 生成器表达式 ---")

# 用 () 而不是 [], 惰性生成, 不占内存
gen = (x**2 for x in range(10))
print(f"  生成器对象: {gen}")
print(f"  取前 3 个: {next(gen)}, {next(gen)}, {next(gen)}")
print(f"  剩下的: {list(gen)}")

# 大小对比
import sys
list_comp = [x**2 for x in range(1000000)]
gen_expr = (x**2 for x in range(1000000))
print(f"\n  列表推导式内存: {sys.getsizeof(list_comp):,} 字节")
print(f"  生成器表达式内存: {sys.getsizeof(gen_expr)} 字节 (几乎不占)")

# ============================================================
# 5. 嵌套推导式
# ============================================================
print("\n--- 嵌套推导式 ---")

# 展平二维列表
matrix = [[1, 2], [3, 4], [5, 6]]
flat = [item for row in matrix for item in row]
print(f"  展平: {flat}")

# 等价 for 循环 (更容易理解)
flat2 = []
for row in matrix:
    for item in row:
        flat2.append(item)
print(f"  等价 for: {flat2}")

# 注: 嵌套推导式的执行顺序就是 for 循环的顺序, 从左到右
# [item for row in matrix for item in row]
#  相当于 for row in matrix: for item in row: result.append(item)

# ============================================================
# 6. 推导式最佳实践
# ============================================================
print("\n--- 最佳实践 ---")

# ✓ 好的推导式 (简单, 一目了然)
names = [user["name"] for user in
    [{"name": "Alice"}, {"name": "Bob"}]]
print(f"  简单推导: {names}")

# ✗ 不好的推导式 (太复杂, 应该用 for 循环)
# result = [x for x in range(100) if x % 2 == 0 if x % 5 == 0 if x > 10]
# 这种多层过滤应该用 for + if 链

# 海象运算符 := (Python 3.8+)
# 在推导式中避免重复计算
import math
# 不好: sqrt 算了两次
# roots = [math.sqrt(x) for x in range(10) if math.sqrt(x) > 2]
# 好: sqrt 只算一次
roots = [r for x in range(10) if (r := math.sqrt(x)) > 2]
print(f"  海象运算符: {roots}")

# ============================================================
# 总结
# ============================================================
# - 列表推导式: [x for x in seq if cond]
# - 字典推导式: {k: v for k, v in seq}
# - 集合推导式: {x for x in seq}
# - 生成器表达式: (x for x in seq) —— 惰性, 省内存
# - 简单用推导式, 复杂用 for 循环
# - 海象运算符 := 能在推导式中复用计算结果
