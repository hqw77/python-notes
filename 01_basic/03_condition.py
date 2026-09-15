"""
条件判断 —— 让代码做出选择

【基本语法】

  if 条件:
      代码块
  elif 另一个条件:
      代码块
  else:
      代码块

  Python 用缩进定义代码块 (不用花括号), 缩进必须是 4 个空格 (PEP 8 规范).

【真值判断 (Truthy / Falsy) —— Python 特有的设计】

  在 if 语句中, Python 不要求条件必须是 bool, 任何对象都可以当条件.

  Falsy 值 (以下在 if 中视为 False):
    - 数字: 0, 0.0, 0j
    - 空容器: "", [], {}, (), set(), frozenset()
    - None
    - False (当然)

  其他所有值都是 Truthy:
    - 非 0 数字, 非空字符串, 非空容器, True, 普通对象...

  这意味着你不需要写 if len(lst) > 0:, 直接写 if lst: 就够了.

【短路求值 —— and/or 的惰性计算】

  and: 如果左边为 False, 右边不执行 (因为整体一定为 False)
  or:  如果左边为 True, 右边不执行 (因为整体一定为 True)

  这个特性不只是性能优化, 还可以用来写安全的取值:
    result = data and data.get("key")  # 如果 data 是 None, 不会调 .get()

  Python 的 and/or 返回的是"被求值的那个对象", 不是 True/False:
    0 or "hello"  → "hello"  (0 是 Falsy, 返回右边)
    100 and 200   → 200      (100 是 Truthy, 返回右边)

【match/case —— Python 3.10+ 的模式匹配】

  比 if/elif/else 更强大的分支工具, 可以:
    - 匹配值
    - 匹配类型
    - 解构序列/映射
    - 带守卫条件 (if 子句)
"""

# ============================================================
# 1. if / elif / else 基本语法
# ============================================================
print("--- 基本条件判断 ---")
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"  分数 {score} → 等级 {grade}")

# ============================================================
# 2. 比较运算符与逻辑运算符
# ============================================================
print("\n--- 比较与逻辑 ---")
x, y = 10, 20
print(f"  x == y: {x == y}")
print(f"  x != y: {x != y}")
print(f"  x < y: {x < y}")
print(f"  x > y: {x > y}")

# 逻辑运算
print(f"  x > 5 and y < 30: {x > 5 and y < 30}")     # True
print(f"  x > 15 or y < 10: {x > 15 or y < 10}")    # False
print(f"  not x > 15: {not x > 15}")                 # True

# ============================================================
# 3. 成员运算符与身份运算符
# ============================================================
print("\n--- 成员 in / not in ---")
fruits = ["apple", "banana", "orange"]
print(f"  'apple' in {fruits}: {'apple' in fruits}")
print(f"  'grape' not in {fruits}: {'grape' not in fruits}")

print("\n--- 身份 is / is not ---")
a = [1, 2, 3]
b = a
c = [1, 2, 3]
print(f"  a is b: {a is b}")      # True (同一个对象)
print(f"  a is c: {a is c}")      # False (不同对象)
print(f"  a is not c: {a is not c}")

# ============================================================
# 4. 真值判断 (Falsy values)
# ============================================================
print("\n--- Falsy 值 ---")
falsy_values = [0, 0.0, "", [], {}, (), set(), None, False]
for v in falsy_values:
    print(f"  bool({v!r}) = {bool(v)}")

print("\n  if lst: 代替 if len(lst) > 0:")
items = []
if not items:           # Pythonic 写法
    print("    列表为空")
# 不推荐: if len(items) == 0:  ← 啰嗦且慢

# ============================================================
# 5. 三元表达式
# ============================================================
print("\n--- 三元表达式 ---")
age = 18
status = "成年" if age >= 18 else "未成年"
print(f"  age={age} → {status}")

# 等价于:
# if age >= 18:
#     status = "成年"
# else:
#     status = "未成年"

# ============================================================
# 6. 短路求值
# ============================================================
print("\n--- 短路求值 ---")

def yes(): print("    yes() 被调用"); return True
def no():  print("    no() 被调用"); return False

print("  no() and yes():")
result = no() and yes()    # yes() 不会被执行!
print(f"    结果: {result}")

print("  yes() or no():")
result = yes() or no()     # no() 不会被执行!
print(f"    结果: {result}")

# and/or 返回的是对象, 不是 True/False
print(f"\n  0 or 'hello' = {0 or 'hello'!r}")
print(f"  100 and 200 = {100 and 200}")
print(f"  '' or 'default' = {'' or 'default'!r}")

# ============================================================
# 7. match / case (Python 3.10+)
# ============================================================
print("\n--- match/case ---")

def handle_command(command):
    match command.split():
        case ["quit"]:
            return "退出"
        case ["help"]:
            return "帮助信息"
        case ["add", a, b]:           # 解构列表
            return f"结果: {int(a) + int(b)}"
        case _:                        # _ 匹配任何东西
            return "未知命令"

print(f"  'quit' → {handle_command('quit')!r}")
print(f"  'add 3 5' → {handle_command('add 3 5')!r}")
print(f"  'xyz' → {handle_command('xyz')!r}")

# ============================================================
# 8. 实用技巧: all() / any()
# ============================================================
print("\n--- all() / any() ---")
# all(): 所有条件都满足
numbers = [10, 20, 30]
if all(n > 0 for n in numbers):
    print("  所有数字都大于 0")

# any(): 任意一个条件满足
if any(n > 25 for n in numbers):
    print("  至少有一个数字大于 25")

# 用 in 代替多个 or (更简洁更易维护)
fruit = "apple"
if fruit == "apple" or fruit == "banana" or fruit == "orange":  # 啰嗦
    pass

if fruit in ("apple", "banana", "orange"):   # 简洁
    print(f"  {fruit} 在列表中")

# ============================================================
# 总结
# ============================================================
# - if/elif/else, 缩进定义代码块
# - Falsy 值: 0, "", [], {}, (), None, False
# - if lst: 代替 if len(lst) > 0: (Pythonic)
# - 三元表达式: x if cond else y
# - 短路求值: and/or 左边决定后, 右边不执行
# - match/case: Python 3.10+ 的模式匹配
# - all()/any() 检查多个条件
