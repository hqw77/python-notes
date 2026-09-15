"""
函数 —— 代码复用的基本单元

【函数是什么?】

  函数 = 带名字的代码块, 接收输入, 返回输出.
  def function_name(parameters):
      ...

  函数是 Python 的"一等公民": 可以赋值给变量, 作为参数传递, 作为返回值返回.
  这是理解装饰器, 闭包, 回调等进阶概念的基础.

【参数传递的真相 —— 传对象引用】

  Python 的参数传递既不是"传值"也不是"传引用", 而是"传对象引用".
  意思是: 形参拿到的是实参指向的那个对象的一个引用 (标签).

  对于不可变对象 (int, str, tuple): 函数内修改形参不会影响实参
  对于可变对象 (list, dict): 函数内修改对象内容会影响实参

  很多人把这个叫"传值"或"传引用", 但严格来说都不准确.

【参数的六种形式】

  def func(a, b=10, *args, c, d=20, **kwargs):
           ^  ^^^^   ^^^^^^  ^^^^^^^^  ^^^^^^^^
           │    │      │        │          └─ 关键字参数字典
           │    │      │        └─ 仅限关键字参数
           │    │      └─ 多余位置参数元组
           │    └─ 默认参数
           └─ 位置参数

  定义顺序必须是: 位置参数 → *args → 仅限关键字参数 → **kwargs

【作用域: LEGB 规则】

  查找变量时, Python 按以下顺序搜索:
    L (Local):      函数内部
    E (Enclosing):  外层函数 (如果有嵌套)
    G (Global):     模块级别
    B (Built-in):   内置命名空间 (print, len, range 等)

  global 关键字: 在函数内声明要修改的是全局变量
  nonlocal 关键字: 在嵌套函数内声明要修改的是外层函数的变量
"""

# ============================================================
# 1. 函数定义与调用
# ============================================================
print("--- 基本函数 ---")

def greet(name):
    """这是一个文档字符串 (docstring)"""
    return f"Hello, {name}!"

print(f"  {greet('Alice')}")
print(f"  函数名: {greet.__name__}")
print(f"  文档: {greet.__doc__}")

# ============================================================
# 2. 参数类型示例
# ============================================================
print("\n--- 参数类型 ---")

def demonstrate_params(pos, default="默认值", *args, keyword_only, **kwargs):
    """展示各种参数类型"""
    print(f"    pos: {pos}")
    print(f"    default: {default}")
    print(f"    *args: {args}")
    print(f"    keyword_only: {keyword_only}")
    print(f"    **kwargs: {kwargs}")

print("  调用:")
demonstrate_params(1, "改过的默认", "多余1", "多余2", keyword_only="必传关键字", extra="额外1", more="额外2")

# ============================================================
# 3. 默认参数的陷阱!
# ============================================================
print("\n--- 默认参数陷阱 ---")

def bad_append(item, target=[]):       # 不要用可变对象作为默认值!
    target.append(item)
    return target

print(f"  第 1 次调用: {bad_append(1)}")   # [1]
print(f"  第 2 次调用: {bad_append(2)}")   # [1, 2] !!! 不是 [2] !!!
print(f"  第 3 次调用: {bad_append(3)}")   # [1, 2, 3] !!!

# 原因: 默认值 [] 只在函数定义时创建一次, 后续调用都共享同一个列表.

# 正确做法:
def good_append(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target

print(f"  good: {good_append(1)}, {good_append(2)}, {good_append(3)}")

# ============================================================
# 4. 参数传递: 可变 vs 不可变
# ============================================================
print("\n--- 参数传递 ---")

def modify_int(n):
    n = 999                     # 只改了局部变量, 不影响外部

def modify_list(lst):
    lst.append(999)             # 改了对象内容, 影响外部!

x = 10
modify_int(x)
print(f"  不可变 int 传递后: x = {x}")    # 10 (不变)

lst = [1, 2, 3]
modify_list(lst)
print(f"  可变 list 传递后: lst = {lst}")   # [1, 2, 3, 999] (被改了!)

# ============================================================
# 5. 作用域: global 与 nonlocal
# ============================================================
print("\n--- 作用域 ---")

global_var = "我是全局变量"

def outer():
    outer_var = "我是外层变量"

    def inner():
        nonlocal outer_var          # 声明要修改外层变量
        outer_var = "被 inner 修改了"
        return outer_var

    inner()
    print(f"  outer_var 修改后: {outer_var}")

outer()
print(f"  global_var 还在: {global_var}")

# ============================================================
# 6. lambda 匿名函数
# ============================================================
print("\n--- lambda ---")

# 普通函数
def add(x, y):
    return x + y

# lambda 等价写法
add_lambda = lambda x, y: x + y

print(f"  add(3, 5) = {add(3, 5)}")
print(f"  lambda 版本: {add_lambda(3, 5)}")

# 常用场景: sorted 的 key 参数
students = [("Alice", 90), ("Bob", 85), ("Charlie", 95)]
sorted_students = sorted(students, key=lambda s: s[1])  # 按分数排序
print(f"  按分数排序: {sorted_students}")

# ============================================================
# 7. map / filter / reduce
# ============================================================
print("\n--- map / filter / reduce ---")

nums = [1, 2, 3, 4, 5]

# map: 每个元素做变换
squared = list(map(lambda x: x**2, nums))
print(f"  map 平方: {squared}")

# filter: 筛选满足条件的元素
even = list(filter(lambda x: x % 2 == 0, nums))
print(f"  filter 偶数: {even}")

# reduce: 累积计算
from functools import reduce
total = reduce(lambda acc, x: acc + x, nums)
print(f"  reduce 求和: {total}")

# 注意: 在现代 Python 中, 列表推导式通常比 map/filter 更可读:
squared2 = [x**2 for x in nums]
even2 = [x for x in nums if x % 2 == 0]
print(f"  列表推导式 (更推荐): squared={squared2}, even={even2}")

# ============================================================
# 总结
# ============================================================
# - 函数是一等公民: 可赋值, 传参, 返回
# - 参数: 位置 → *args → 仅限关键字 → **kwargs
# - 默认参数不要用可变对象 ([] / {})
# - 参数传递是"传对象引用"
# - 作用域: LEGB (Local → Enclosing → Global → Built-in)
# - global / nonlocal 声明要修改外层变量
# - lambda: 简单的匿名函数, 常用于 sorted(key=...) 等
# - 能用列表推导式就不用 map/filter
