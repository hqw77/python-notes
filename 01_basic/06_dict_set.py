"""
字典与集合 —— 基于哈希表的高效数据结构

【字典是什么?】

  字典是"键值对"的集合, 底层基于哈希表.
  你可以把它当成一个超级快的查找表: 给定 key, O(1) 时间找到 value.

  O(1) 意味着不管字典里有一千条还是一千万条数据, 查一条的时间几乎一样.

【为什么字典这么快? —— 哈希表原理简述】

  1. Python 对 key 调用 hash(key), 得到一个整数
  2. 用这个整数计算出一个数组下标
  3. 直接去那个位置取数据

  所以查找不用遍历, 直接"算"出位置. 代价是:
    - key 必须是"可哈希"的 (不可变类型: int, str, tuple, frozenset)
    - list 和 dict 不能作为 key (因为可变, 哈希值会变)

【集合是什么?】

  集合就是"只有 key, 没有 value 的字典".
  所以它也有 O(1) 查找, 元素也必须是可哈希的.
  集合自动去重, 常用于:
    - 去重: set([1, 2, 2, 3]) → {1, 2, 3}
    - 成员检查: x in set → O(1), 比 list 的 O(n) 快得多
    - 集合运算: 交集, 并集, 差集

【Python 3.7+: dict 是有序的】

  从 Python 3.7 开始, dict 保证按插入顺序迭代.
  这是 CPython 3.6 的实现细节升级为语言保证.
  不需要 OrderedDict 了 (除非你需要按 key 移动顺序).
"""

from collections import defaultdict

# ============================================================
# 1. 字典创建与基本操作
# ============================================================
print("--- 字典创建 ---")
d1 = {"a": 1, "b": 2}
d2 = dict(a=1, b=2)
d3 = dict([("a", 1), ("b", 2)])
print(f"  d1 = {d1}")
print(f"  d2 = {d2}")
print(f"  d3 = {d3}")

print("\n--- 基本操作 ---")
d = {"name": "Alice", "age": 30}
d["city"] = "Beijing"              # 新增
d["age"] = 31                       # 修改
print(f"  新增/修改后: {d}")
del d["city"]                        # 删除
print(f"  删除 city 后: {d}")

# ============================================================
# 2. 安全取值: get() vs []
# ============================================================
print("\n--- 安全取值 ---")
user = {"name": "Bob"}
# print(user["age"])    # KeyError! 程序崩溃
age = user.get("age")        # 返回 None, 不报错
age_default = user.get("age", 0)  # 如果不存在, 返回默认值 0
print(f"  get('age') = {age}")
print(f"  get('age', 0) = {age_default}")
print(f"  get('name') = {user.get('name')}")

# ============================================================
# 3. 字典方法
# ============================================================
print("\n--- 常用方法 ---")
d = {"a": 1, "b": 2}
print(f"  keys: {list(d.keys())}")
print(f"  values: {list(d.values())}")
print(f"  items: {list(d.items())}")

# setdefault: 有就返回, 没有就设置一个默认值
d = {"a": 1}
val = d.setdefault("b", 99)   # b 不存在, 设置为 99
print(f"  setdefault('b', 99) → {val}, d = {d}")

# ============================================================
# 4. 字典合并
# ============================================================
print("\n--- 字典合并 ---")
d1 = {"a": 1, "b": 2}
d2 = {"b": 99, "c": 3}     # b 冲突了

# 方式一: update (原地修改)
d1_copy = d1.copy()
d1_copy.update(d2)
print(f"  update 合并: {d1_copy}")    # b=99, d2 覆盖 d1

# 方式二: | 运算符 (Python 3.9+, 返回新字典)
merged = d1 | d2
print(f"  | 合并: {merged}")          # b=99

# 方式三: ** 解包
merged2 = {**d1, **d2}
print(f"  ** 解包: {merged2}")        # b=99

# ============================================================
# 5. defaultdict
# ============================================================
print("\n--- defaultdict ---")
# 普通 dict: 统计词频需要先检查 key 是否存在
words = ["a", "b", "a", "c", "b", "a"]
count1 = {}
for w in words:
    if w not in count1:
        count1[w] = 0
    count1[w] += 1
print(f"  普通 dict: {count1}")

# defaultdict: 自动给新 key 一个默认值
count2 = defaultdict(int)          # int() = 0
for w in words:
    count2[w] += 1                  # 不需要检查 key 是否存在!
print(f"  defaultdict(int): {dict(count2)}")

# 按首字母分组
names = ["Alice", "Bob", "Anna", "Bill"]
groups = defaultdict(list)         # list() = []
for name in names:
    groups[name[0]].append(name)
print(f"  按首字母分组: {dict(groups)}")

# ============================================================
# 6. 集合
# ============================================================
print("\n--- 集合 ---")

# 创建
s1 = {1, 2, 3}
s2 = set([1, 2, 2, 3, 3])        # 自动去重
print(f"  {s2 = }")

# 去重 (经典用法)
lst = [1, 2, 2, 3, 3, 3]
unique = list(set(lst))
print(f"  去重 {lst} → {unique}")

print("\n--- 集合运算 ---")
a = {1, 2, 3}
b = {2, 3, 4}
print(f"  a = {a}, b = {b}")
print(f"  a | b (并集) = {a | b}")
print(f"  a & b (交集) = {a & b}")
print(f"  a - b (差集) = {a - b}")
print(f"  a ^ b (对称差集) = {a ^ b}")     # 在 a 或 b, 但不同时在两者

print("\n--- 集合方法 ---")
s = {1, 2}
s.add(3)                           # 添加
print(f"  add(3) → {s}")
s.discard(99)                       # 删除, 不存在也不报错 (推荐)
# s.remove(99)                      # 删除, 不存在报 KeyError
print(f"  discard(99) 不报错: {s}")
print(f"  2 in {s}: {2 in s}")     # O(1) 成员检查

# frozenset: 不可变集合, 可哈希, 能当 dict key
fs = frozenset([1, 2, 3])
d = {fs: "frozen key"}
print(f"\n  frozenset 作为 dict key: {d}")

# ============================================================
# 总结
# ============================================================
# - dict: 键值对, O(1) 查找, key 必须可哈希
# - get(key, default) > dict[key] (安全, 不报 KeyError)
# - dict 合并: | 运算符 (3.9+), ** 解包, update()
# - defaultdict: 新 key 自动有默认值
# - set: 去重, 集合运算, O(1) 成员检查
# - frozenset: 不可变集合, 能当 dict key
# - set 没有顺序 (和 dict 不一样)
