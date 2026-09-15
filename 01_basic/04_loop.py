"""
循环 —— for / while / break / continue

【两种循环, 两种场景】

  for:   知道要遍历什么 (一个序列, 一个范围), "对一个集合里的每个元素做..."
  while: 知道什么时候停 (一个条件), "当条件满足时一直做..."

  能用 for 就不用 while -- for 更安全 (不会死循环), 更可读.

【for 循环的本质】

  for x in obj: 的底层:
    1. 调用 iter(obj) 获取迭代器
    2. 反复调用 next(iterator) 获取下一个值
    3. 遇到 StopIteration 异常时停止

  所以 for 循环不限于 list/str, 任何可迭代对象都能 for.
  (详见 03_advanced/iterator.py)

【range -- 不是 list!】

  range(5) 不返回 [0, 1, 2, 3, 4], 它返回一个 range 对象.
  range 是惰性的: 只在需要时产生下一个数字, 占用固定内存.

  range(start, stop, step):
    range(5)       → 0, 1, 2, 3, 4
    range(2, 5)    → 2, 3, 4
    range(0, 10, 2)→ 0, 2, 4, 6, 8
    range(5, 0, -1)→ 5, 4, 3, 2, 1

  如果你想得到一个 list: list(range(5)) → [0, 1, 2, 3, 4]

【for-else: Python 独有但少为人知的语法】

  for 循环正常结束 (没被 break) 时, 执行 else 块.
  如果被 break 中断了, 不执行 else.

  典型场景: 搜索
    for item in items:
        if condition:
            print("找到了")
            break
    else:
        print("没找到")
"""

# ============================================================
# 1. for 循环基础
# ============================================================
print("--- for 遍历各种类型 ---")
# list
for x in [1, 2, 3]:
    print(f"  list item: {x}")

# str
for ch in "AB":
    print(f"  str char: {ch!r}")

# dict (默认遍历 keys)
d = {"a": 1, "b": 2}
for k in d:
    print(f"  dict key: {k!r}")

for k, v in d.items():
    print(f"  dict item: {k!r} → {v}")

# ============================================================
# 2. range
# ============================================================
print("\n--- range ---")
print(f"  range(5) = {list(range(5))}")
print(f"  range(2, 5) = {list(range(2, 5))}")
print(f"  range(0, 10, 2) = {list(range(0, 10, 2))}")
print(f"  range(5, 0, -1) = {list(range(5, 0, -1))}")

# range 不是 list, 惰性
r = range(1000000)
print(f"  range(1000000) 占用内存: {r.__sizeof__()} 字节 (list 要 8MB+)")

# ============================================================
# 3. while 循环
# ============================================================
print("\n--- while ---")
count = 0
while count < 3:
    print(f"  count = {count}")
    count += 1

# 小心死循环: while True 如果没有 break 就会一直跑

# ============================================================
# 4. break 与 continue
# ============================================================
print("\n--- break ---")
for i in range(10):
    if i == 3:
        break            # 退出整个循环
    print(f"  {i}", end=" ")
print()

print("\n--- continue ---")
for i in range(5):
    if i == 2:
        continue         # 跳过 2, 继续下一次迭代
    print(f"  {i}", end=" ")
print()

# ============================================================
# 5. for-else: 循环正常结束时执行
# ============================================================
print("\n--- for-else ---")

def search(target, items):
    for item in items:
        if item == target:
            print(f"  找到了 {target}")
            break
    else:                          # 只有没 break 才执行
        print(f"  没找到 {target}")

search(3, [1, 2, 3, 4])           # 找到了
search(99, [1, 2, 3, 4])           # 没找到

# ============================================================
# 6. enumerate / zip / reversed
# ============================================================
print("\n--- enumerate: 同时拿索引和值 ---")
for i, name in enumerate(["Alice", "Bob", "Charlie"]):
    print(f"  [{i}] {name}")

print("\n--- zip: 并行迭代 ---")
names = ["Alice", "Bob", "Charlie"]
scores = [90, 85, 95]
for name, score in zip(names, scores):
    print(f"  {name}: {score}")

# zip 以最短的序列为准
print(f"  zip 不等长: {list(zip('AB', [1, 2, 3]))}")  # [('A', 1), ('B', 2)]

print("\n--- reversed: 反向迭代 ---")
for x in reversed([1, 2, 3]):
    print(f"  {x}", end=" ")
print()

# ============================================================
# 7. 嵌套循环
# ============================================================
print("\n--- 嵌套循环 (九九乘法表) ---")
for i in range(1, 4):
    for j in range(1, 4):
        print(f"    {i}×{j}={i*j}", end="")
    print()

# ============================================================
# 总结
# ============================================================
# - for: 遍历可迭代对象; while: 条件为 True 时重复
# - range 是惰性的, 不是 list
# - break 退出整个循环, continue 跳过本次迭代
# - for-else: 没 break 才执行 else (搜索场景很有用)
# - enumerate 同时拿索引和值, zip 并行迭代多个序列
# - 能用 for 就不用 while
