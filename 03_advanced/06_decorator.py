"""
装饰器 (Decorator)

【什么是装饰器?】

  装饰器是一种在不修改原函数代码的情况下, 给函数增加新功能的方式.
  本质: 一个接收函数作为参数, 返回一个新函数的"高阶函数".

  语法糖:
    @decorator
    def func():
        ...

  等价于:
    func = decorator(func)

  打个比方: 给手机套个壳. 手机本身没变, 但多了保护功能.
  装饰器就是给函数套了个"功能外壳".

【前置知识: 函数是一等公民 + 闭包】

  为什么装饰器能工作? 因为 Python 里:
    1. 函数是"一等公民" — 可以赋值给变量, 作为参数传递, 作为返回值
    2. 闭包 — 内部函数能"记住"外部函数的变量

  一等公民示例:
    def greet(name):
        return f"Hello, {name}"

    g = greet           # 函数赋值给变量
    g("Alice")          # 通过变量调用

    def apply(func, arg):  # 函数作为参数
        return func(arg)

    def make_multiplier(n):  # 函数作为返回值 (闭包)
        def multiplier(x):
            return x * n     # multiplier "记住" 了外部的 n
        return multiplier

【装饰器的执行模型 ── 洋葱模型】

  @timer
  @logger
  def foo():
      ...

  等价于 foo = timer(logger(foo))

  执行顺序 (从外到内, 再从内到外):
    进入 timer → 进入 logger → foo() → 退出 logger → 退出 timer

  像剥洋葱: 最外层的 @timer 最先进入, 最后退出.

【装饰器的三种形式】

  形式                  │ 适用场景
  ──────────────────────┼─────────────────────
  @decorator            │ 无参装饰器, 最简单
  def func(): ...       │
  ──────────────────────┼─────────────────────
  @decorator(args)      │ 带参装饰器, 本质是"装饰器工厂"
  def func(): ...       │ decorator(args) 返回一个真正的装饰器
  ──────────────────────┼─────────────────────
  class Decorator:      │ 类装饰器, 基于 __call__
      def __call__(...) │ 优点: 可以用属性保存状态

【@wraps ── 为什么几乎每个装饰器都要用它?】

  不加 @wraps:
    @bad_decorator
    def my_func():
        \"\"\"文档字符串\"\"\"
        pass
    my_func.__name__  # → "wrapper"  (丢失了原函数名!)
    my_func.__doc__   # → None        (丢失了文档字符串!)

  加了 @wraps(func):
    @good_decorator
    def my_func():
        \"\"\"文档字符串\"\"\"
        pass
    my_func.__name__  # → "my_func"   (正确!)
    my_func.__doc__   # → "文档字符串" (正确!)

  wraps 做的事: 把原函数的 __name__, __doc__, __module__ 等元信息
  复制到 wrapper 函数上. 不用的后果: 调试时函数名全是 wrapper,
  根本分不清哪个是哪个.

【常见用途】

  日志记录    → 自动打印函数名, 参数, 返回值
  计时统计    → 测量函数执行时间
  权限检查    → 执行前验证用户权限
  缓存        → 记住之前的计算结果
  重试机制    → 失败后自动重试
  输入验证    → 检查参数合法性
  注册回调    → 把函数自动加入某个列表
"""

import time
from functools import wraps

# ============================================================
# 0. 前置知识：函数是一等公民 + 闭包
# ============================================================
print("--- 前置：函数是一等公民 ---")

def greet(name):
    return f"Hello, {name}"

# 函数可以赋值给变量
g = greet
print(f"  变量调用: {g('Alice')}")

# 函数可以作为参数传递
def apply(func, arg):
    return func(arg)
print(f"  作为参数: {apply(greet, 'Bob')}")

# 函数可以作为返回值（闭包）
def make_multiplier(n):
    """返回一个把输入乘以 n 的函数"""
    def multiplier(x):
        return x * n           # multiplier "记住" 了外部的 n
    return multiplier

times3 = make_multiplier(3)
times5 = make_multiplier(5)
print(f"  闭包 times3(10): {times3(10)}")   # 30
print(f"  闭包 times5(10): {times5(10)}")   # 50


# ============================================================
# 1. 最简单的装饰器 —— 手动实现
# ============================================================
print("\n--- 手动装饰器 ---")

def my_decorator(func):
    """装饰器：接收函数，返回新函数"""
    def wrapper():
        print("  装饰器添加的前置操作")
        func()
        print("  装饰器添加的后置操作")
    return wrapper

def say_hello():
    print("  Hello World!")

# 手动装饰
say_hello = my_decorator(say_hello)
say_hello()


# ============================================================
# 2. 使用 @ 语法糖
# ============================================================
print("\n--- @ 语法糖 ---")

@my_decorator
def say_bye():
    print("  Bye World!")

# 上面的 @my_decorator 等价于 say_bye = my_decorator(say_bye)
say_bye()


# ============================================================
# 3. 装饰带参数的函数 —— 用 *args **kwargs
# ============================================================
def logger(func):
    """打印函数调用参数的装饰器"""
    def wrapper(*args, **kwargs):
        print(f"  调用 {func.__name__}(args={args}, kwargs={kwargs})")
        result = func(*args, **kwargs)
        print(f"  返回 {result}")
        return result
    return wrapper

@logger
def add(a, b):
    return a + b

print("\n--- 装饰带参函数 ---")
add(3, 5)
add(b=10, a=7)


# ============================================================
# 4. functools.wraps —— 保留原函数的元信息
# ============================================================
print("\n--- functools.wraps ---")

# 没加 wraps 的问题
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@bad_decorator
def my_func():
    """这是文档字符串"""
    pass

print(f"  没 wraps: 名字={my_func.__name__}, 文档={my_func.__doc__}")
# 输出: wrapper, None —— 元信息丢失了!

# 加了 wraps
def good_decorator(func):
    @wraps(func)                   # 把 func 的元信息复制到 wrapper
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@good_decorator
def my_func2():
    """这是文档字符串"""
    pass

print(f"  有 wraps: 名字={my_func2.__name__}, 文档={my_func2.__doc__}")
# 输出: my_func2, 这是文档字符串 —— 正确保留！


# ============================================================
# 5. 实用装饰器一：计时器
# ============================================================
print("\n--- 计时器装饰器 ---")

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"  {func.__name__} 耗时: {elapsed:.6f} 秒")
        return result
    return wrapper

@timer
def slow_sum(n):
    return sum(range(n))

# slow_sum(10_000_000)
#     ↓
# 发现被 @timer 装饰，实际调用 wrapper(10_000_000)
#     ↓
# wrapper 内部：
#     1. 记录开始时间
#     2. 通过持有的 func 引用，去执行真正的 slow_sum(10_000_000)
#        └── 内部执行 sum(range(n))，计算出结果 49999995000000
#     3. 记录结束时间，打印耗时
#     4. return result  (把巨大的数字交还给调用者)
#     ↓
# 因为调用者没写 `x = slow_sum(...)`，这个返回的巨大数字被 Python 解释器直接丢弃（内存释放）
#     ↓
# 屏幕上只留下装饰器里的 print 输出的耗时日志
slow_sum(10_000_000)



# ============================================================
# 6. 实用装饰器二：重试机制
# ============================================================
# 带参数的装饰器 = "装饰器工厂". 你写的 @retry(max_attempts=3) 其实是两步:
#   第 1 步: retry(max_attempts=3) 被调用 → 返回 decorator 函数
#   第 2 步: @decorator 把 unreliable_function 传入 → 返回 wrapper
#
# 展开来就是: unreliable_function = retry(max_attempts=3)(unreliable_function)
#                    ↑                        ↑                    ↑
#                 最终结果           第1步: 调用工厂      第2步: 传入原函数

import random

def retry(max_attempts=3):
    """装饰器工厂: 接收参数, 返回一个真正的装饰器"""
    def decorator(func):
        """真正的装饰器: 接收函数, 返回 wrapper"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            """wrapper: 包装原函数, 失败时重试"""
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"    第 {attempt} 次失败: {e}")
                    if attempt == max_attempts:
                        raise       # 最后一次也失败了 → 放弃, 抛异常
            return None
        return wrapper
    return decorator

print("\n--- 重试装饰器 ---")

call_count = 0

@retry(max_attempts=3)                   # ← 工厂先执行, 返回装饰器, 装饰器再执行
def unreliable_function():
    global call_count
    call_count += 1
    if call_count < 3:                   # 前 2 次故意失败
        raise ValueError(f"模拟失败 (第{call_count}次)")
    return "成功!"

# ====================================
# 第 0 步: 定义装饰器工厂
# ====================================
def retry(max_attempts=3):
    def decorator(func):                # ← func 在这里: 被闭包"记住"
        @wraps(func)
        def wrapper(*args, **kwargs):   # ← *args, **kwargs 收集所有传入的参数
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)  # ← 把参数原样传给原函数
                except Exception as e:
                    if attempt == max_attempts:
                        raise
        return wrapper
    return decorator


# ====================================
# 第 1 步: @retry(3) 执行
# ====================================
# retry(3) 被调用 → 返回 decorator 函数
# max_attempts=3 被闭包记住

# ====================================
# 第 2 步: @decorator 执行
# ====================================
# decorator(unreliable_function) 被调用 → 返回 wrapper
# func = unreliable_function 被闭包记住 (就在 decorator 的 func 参数里!)

# ====================================
# 第 3 步: 变量名被替换
# ====================================
# unreliable_function = wrapper
#       ↑                      ↑
#    这个名字现在           指向 wrapper 函数
#    指向 wrapper

# ====================================
# 第 4 步: 调用 unreliable_function()
# ====================================
# 你写: unreliable_function()
# 实际执行: wrapper()
#     ↓
# wrapper 内部:
#   for attempt in 1..3:
#       try:
#           return func()          ← 这里的 func 就是被闭包记住的原函数!
#       except:
#           ...




# 执行流程追踪:
# unreliable_function()
#     ↓
# 发现被 @retry(3) 装饰, 实际调用 wrapper()
#     ↓
# wrapper 内部 (attempt 从 1 到 3):
#     attempt=1: 调用 func() → 抛 ValueError → 打印失败 → continue
#     attempt=2: 调用 func() → 抛 ValueError → 打印失败 → continue
#     attempt=3: 调用 func() → call_count=3, 不再抛异常 → 返回 "成功!"
#     ↓
# 返回 "成功!"

print(f"  结果: {unreliable_function()}")


# ============================================================
# 7. 实用装饰器三：权限检查
# ============================================================
# 和重试装饰器一样, @require_auth(user) 也是"装饰器工厂"模式.
# require_auth(admin_user) → 返回 decorator → @decorator 装饰函数
#
# 关键点: user 在定义装饰器时就固定了! admin_user 和 normal_user 是
# 两个不同的字典, 分别传入 require_auth, 产生两个不同的 decorator,
# 两个 decorator 又分别固定了自己看到的 user.

def require_auth(user):
    """装饰器工厂: 用给定的 user 检查权限. user 被闭包"记住"."""
    def decorator(func):
        """接收被装饰的函数"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if user.get("is_admin"):             # 检查闭包记住的 user
                return func(*args, **kwargs)      # 有权限 → 正常执行
            else:
                print(f"  权限不足: {user.get('name')} 不能执行 {func.__name__}")
                return None                       # 无权限 → 返回 None
        return wrapper
    return decorator

print("\n--- 权限检查装饰器 ---")

admin_user = {"name": "管理员", "is_admin": True}
normal_user = {"name": "普通用户", "is_admin": False}

@require_auth(admin_user)                # user=admin_user 被闭包记住
def delete_post(post_id):
    print(f"  帖子 {post_id} 已删除")

@require_auth(normal_user)               # user=normal_user 被闭包记住
def create_post(title):
    print(f"  帖子 '{title}' 已创建")

# 执行流程追踪:
# delete_post(123)
#     ↓
# 发现被 @require_auth(admin_user) 装饰, 实际调用 wrapper(123)
#     ↓
# wrapper 内部:
#     user = admin_user (闭包记住的)
#     user.get("is_admin") → True → 有权限
#     执行 func(123) → print("帖子 123 已删除")
#     ↓
# 成功执行!

# create_post("新帖子")
#     ↓
# 发现被 @require_auth(normal_user) 装饰, 实际调用 wrapper("新帖子")
#     ↓
# wrapper 内部:
#     user = normal_user (闭包记住的)
#     user.get("is_admin") → False → 无权限
#     print("权限不足...") → return None
#     ↓
# 被拒绝执行!

delete_post(123)          # 成功
create_post("新帖子")       # 权限不足


# ============================================================
# 8. 装饰器可以叠加
# ============================================================
print("\n--- 装饰器叠加 ---")

@timer
@logger
def multiply(a, b):
    return a * b

# 等价于 multiply = timer(logger(multiply))
# 执行顺序（洋葱模型）：timer → logger → multiply → logger → timer
result = multiply(6, 7)
print(f"  最终结果: {result}")


# ============================================================
# 9. 类装饰器（复习：你在 03_callable.py 已见过）
# ============================================================
class CountCalls:
    """统计函数被调用次数的装饰器"""
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"  {self.func.__name__} 被调用了 {self.count} 次")
        return self.func(*args, **kwargs)

print("\n--- 类装饰器 ---")

@CountCalls
def greet(name):
    print(f"    Hello, {name}!")

greet("Alice")
greet("Bob")


# ============================================================
# 总结
# ============================================================
# 本质: 装饰器 = 接收函数 + 返回新函数
# @decorator 等价于 func = decorator(func)
# @wraps 保留原函数的 __name__ __doc__ 等元信息
# 带参数的装饰器 = 装饰器工厂：函数返回装饰器，装饰器再返回 wrapper
# 执行顺序：洋葱模型，从外到内进入，从内到外退出
# 常见用途：日志、计时、权限、缓存、重试、输入验证
