"""
列表与元组 —— Python 最常用的序列类型

【核心区别: 可变 vs 不可变】

  ┌────────────┬──────────┬──────────────────────────────┐
  │            │ list     │ tuple                         │
  ├────────────┼──────────┼──────────────────────────────┤
  │ 创建语法    │ [1,2,3]  │ (1,2,3) 或 1,2,3             │
  │ 可变性      │ 可变      │ 不可变 (创建后不能改)          │
  │ 方法数      │ 10+      │ 只有 count() 和 index()       │
  │ 作为 dict key│ 不行     │ 可以 (因为不可变 = 可哈希)    │
  │ 速度        │ 稍慢      │ 稍快                         │
  │ 内存        │ 稍大      │ 稍小                         │
  │ 适用场景    │ 数据需要增删改 │ 数据不变 (坐标, 配置, 字典 key) │
  └────────────┴──────────┴──────────────────────────────┘

【什么时候用 tuple?】

  1. 数据不应该被修改 (保护数据): 坐标 (x, y), RGB 颜色 (255, 0, 0)
  2. 作为 dict 的 key: 复合键, 如 {(x, y): value}
  3. 函数返回多个值: 实际返回的是一个 tuple
  4. 拆包: a, b = (1, 2)

【可变对象的引用陷阱】

  列表是可变对象, 赋值是传引用, 不是复制:
    a = [1, 2, 3]
    b = a         # b 和 a 指向同一个列表!
    b.append(4)   # a 也被修改了! a = [1, 2, 3, 4]

  解决方法: 用 copy() (浅拷贝) 或 deepcopy() (深拷贝)

【拆包 (Unpacking)】

  把一个序列的元素分别赋给多个变量:
    a, b, c = [1, 2, 3]
    head, *tail = [1, 2, 3, 4]    # head=1, tail=[2,3,4]
    *head, tail = [1, 2, 3, 4]    # head=[1,2,3], tail=4
"""

from collections import namedtuple
import copy

# ============================================================
# 1. 列表创建与基本操作
# ============================================================
print("--- 列表创建 ---")
lst1 = [1, 2, 3]
lst2 = list("abc")          # 从可迭代对象创建
lst3 = list(range(5))
print(f"  [1, 2, 3] = {lst1}")
print(f"  list('abc') = {lst2}")
print(f"  list(range(5)) = {lst3}")

print("\n--- 索引与切片 ---")
print(f"  lst1[0] = {lst1[0]}")
print(f"  lst1[-1] = {lst1[-1]}")
print(f"  lst1[1:] = {lst1[1:]}")
print(f"  lst1[::-1] = {lst1[::-1]}")     # 反转

# ============================================================
# 2. 列表方法
# ============================================================
print("\n--- 增删改 ---")
fruits = ["apple", "banana"]
fruits.append("orange")              # 尾部追加
print(f"  append: {fruits}")
fruits.insert(1, "grape")            # 指定位置插入
print(f"  insert(1): {fruits}")
fruits.remove("banana")              # 按值删除 (只删第一个)
print(f"  remove: {fruits}")
popped = fruits.pop()                # 按索引删除, 不传参删最后一个; 返回被删的值
print(f"  pop(): {popped}, 剩下: {fruits}")
fruits.extend(["kiwi", "mango"])    # 批量追加 (和 append 的区别: append 会把整个列表当一个元素)
print(f"  extend: {fruits}")

print("\n--- 查找与统计 ---")
nums = [3, 1, 4, 1, 5]
print(f"  nums: {nums}")
print(f"  nums.index(4) = {nums.index(4)}")        # 4 的索引
print(f"  nums.count(1) = {nums.count(1)}")         # 1 出现了几次

print("\n--- 排序 ---")
nums.sort()                          # 原地排序
print(f"  nums.sort(): {nums}")
nums.sort(reverse=True)              # 降序
print(f"  nums.sort(reverse=True): {nums}")

# sorted() vs list.sort()
original = [3, 1, 2]
new = sorted(original)               # 返回新列表, 原列表不变
print(f"  sorted({original}) = {new}, 原列表不变: {original}")

# ============================================================
# 3. 可变引用与拷贝
# ============================================================
print("\n--- 引用陷阱 ---")
a = [1, 2, 3]
b = a                                # b 和 a 指向同一个列表
b.append(4)
print(f"  a={a}, b={b}  ← 改 b 也改了 a!")

print("\n--- 浅拷贝 vs 深拷贝 ---")
a = [[1, 2], [3, 4]]
b = a.copy()                         # 浅拷贝: 只拷贝外层
b[0][0] = 99
print(f"  浅拷贝后改嵌套元素: a={a}, b={b}  ← 内层还是共享的!")

a = [[1, 2], [3, 4]]
c = copy.deepcopy(a)                 # 深拷贝: 外层内层全部复制
c[0][0] = 99
print(f"  深拷贝后改嵌套元素: a={a}, c={c}  ← 完全独立!")

# ============================================================
# 4. 拆包 (Unpacking)
# ============================================================
print("\n--- 拆包 ---")
a, b, c = [1, 2, 3]
print(f"  a,b,c = [1,2,3] → a={a}, b={b}, c={c}")

# * 收集剩余元素
head, *tail = [1, 2, 3, 4, 5]
print(f"  head={head}, tail={tail}")

first, *middle, last = [1, 2, 3, 4, 5]
print(f"  first={first}, middle={middle}, last={last}")

# ============================================================
# 5. 元组
# ============================================================
print("\n--- 元组 ---")
t1 = (1, 2, 3)
t2 = 1, 2, 3           # 括号可省略
t3 = (42,)             # 单元素元组必须有逗号! (42) 就是 int 了
print(f"  t1={t1}, t2={t2}, t3={t3}")
print(f"  type((42)) = {type((42)).__name__}")     # int! 不是 tuple
print(f"  type((42,)) = {type((42,)).__name__}")   # tuple

# 元组不可变
try:
    t1[0] = 99
except TypeError as e:
    print(f"  t1[0] = 99 → TypeError: {e}")

# 元组拆包 (经典用法: 交换变量)
x, y = 10, 20
x, y = y, x            # 交换! 右边先创建 tuple (20, 10), 然后拆包
print(f"  交换后: x={x}, y={y}")

# ============================================================
# 6. namedtuple
# ============================================================
print("\n--- namedtuple ---")
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(f"  p = {p}")
print(f"  p.x = {p.x}, p.y = {p.y}")
print(f"  p[0] = {p[0]}, p[1] = {p[1]}")    # 也能用索引访问

# 元组作为 dict key
d = {p: "坐标点"}
print(f"  dict key: {d}")

# ============================================================
# 总结
# ============================================================
# - list: 可变, 适合需要增删改的数据
# - tuple: 不可变, 适合固定数据, dict key, 函数返回多值
# - 列表是引用传递: a = b 不复制, 改 b 影响 a
# - copy() 浅拷贝, deepcopy() 深拷贝
# - 拆包: a, *rest, b = seq
# - sorted() 返回新列表, .sort() 原地排序
# - 单元素元组: (x,), 必须有逗号
