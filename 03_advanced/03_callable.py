"""
可调用协议 -- __call__

[什么是"可调用"?]

  Python 中, 能加 () 执行的东西都叫"可调用对象" (callable):
    - 函数          def foo(): ...     foo()
    - lambda        lambda x: x + 1    (lambda x: x+1)(3)
    - 类            MyClass()          调用类 = 创建实例
    - 方法          obj.method()       绑定到实例的函数
    - 有 __call__ 的实例  obj()        实例本身像函数一样调用

  callable(obj) 可以检测一个对象是否可调用.

[__call__ 解决了什么问题?]

  普通函数是"无状态"的--每次调用完, 内部变量就消失了.
  但有时候你需要一个"带记忆的函数":
    例1: 计数器--每次调用数字+1, 需要记住当前计数
    例2: 缓存函数--记住之前算过的结果
    例3: 策略对象--不同的折扣算法, 但调用方式一样: discount(price)

  传统的做法是用闭包:
    def make_counter():
        count = 0
        def inner():
            nonlocal count
            count += 1
            return count
        return inner
    counter = make_counter()

  __call__ 的做法更直观, 更容易扩展:
    class Counter:
        def __init__(self):
            self.count = 0
        def __call__(self):
            self.count += 1
            return self.count
    counter = Counter()

  两种写法等价, 但类的版本可以加更多方法, 属性, 更容易维护.

[调用链路 -- counter() 时发生了什么?]

  当你写 counter() 时:
    1. Python 检测到 counter 是一个实例 (不是函数)
    2. Python 去找 type(counter).__call__(counter)
    3. 也就是 Counter.__call__(counter)
    4. 执行你定义的 __call__ 方法体

  这和你写 obj.method() 是一样的查找逻辑, 只是特殊的名字 __call__ 让 () 能触发.

[典型应用场景]

  场景              │ 为什么用 __call__ 而不是普通方法
  ──────────────────┼──────────────────────────────
  计数器            │ counter()  比 counter.increment() 更自然
  带参函数工厂       │ add5(10)   创建"加了固定数"的函数
  缓存装饰器         │ memo(func) 返回一个带缓存的可调用对象
  策略模式          │ discount(price) 所有策略同一调用方式
  状态机            │ state(input) 每个状态是一个可调用对象
  中间件/管道        │ middleware(request) 统一调用接口

  __call__ 的核心优势: 让你的对象"像函数一样"被使用,
  但它有 self, 所以能访问自己的属性 (状态), 也能拥有其他方法.

[运行方式]
  全部: python 03_callable.py
  单个: python 03_callable.py counter / adder / memoize / strategy / decorator / check_callable
"""

from functools import partial


# ============================================================
# 1. 基础示例 -- 带状态的函数
# ============================================================
def demo_counter():
    class Counter:
        """每次调用计数器加 1 -- 保存调用次数这个"状态" """
        def __init__(self):
            self.count = 0

        def __call__(self):
            self.count += 1
            return self.count

    counter = Counter()
    print("--- 可调用计数器 ---")
    print(f"  第 1 次调用: {counter()}")   # 1 -- 注意是 counter() 不是 counter.xxx()
    print(f"  第 2 次调用: {counter()}")   # 2
    print(f"  第 3 次调用: {counter()}")   # 3


# ============================================================
# 2. 带参数的 __call__
# ============================================================
def demo_adder():
    class Adder:
        """创建一个"加了固定数"的函数"""
        def __init__(self, n):
            self.n = n

        def __call__(self, x):
            return x + self.n

    add5 = Adder(5)
    add10 = Adder(10)
    print(f"\n--- 带参数的可调用对象 ---")
    print(f"  add5(10) = {add5(10)}")     # 15
    print(f"  add10(10) = {add10(10)}")   # 20

    # 等价于偏函数 (但更灵活)
    add5_partial = partial(lambda n, x: x + n, 5)
    print(f"  partial 版本: {add5_partial(10)}")


# ============================================================
# 3. 实用案例: 缓存函数的结果
# ============================================================
def demo_memoize():
    class Memoize:
        """记住每次调用的结果, 相同输入直接返回缓存 (不用重算)"""
        def __init__(self, func):
            self.func = func
            self.cache = {}

        def __call__(self, *args):
            if args not in self.cache:
                self.cache[args] = self.func(*args)
                print(f"    计算 {args} -> {self.cache[args]}")
            else:
                print(f"    命中缓存 {args} -> {self.cache[args]}")
            return self.cache[args]

    def expensive_calc(x):
        import time
        time.sleep(0.1)
        return x ** 2

    memo_calc = Memoize(expensive_calc)
    print("\n--- 带缓存的函数 ---")
    memo_calc(10)    # 计算
    memo_calc(10)    # 命中缓存
    memo_calc(20)    # 计算


# ============================================================
# 4. 实用案例: 策略模式
# ============================================================
def demo_strategy():
    class Discount:
        """折扣策略 -- 每种折扣是一个可调用对象"""
        def __init__(self, rate, name):
            self.rate = rate
            self.name = name

        def __call__(self, price):
            result = price * (1 - self.rate)
            print(f"  {self.name}: {price} -> {result:.2f}")
            return result

    print("\n--- 策略模式 ---")
    strategies = [
        Discount(0.1, "九折"),
        Discount(0.2, "八折"),
        Discount(0.5, "五折"),
    ]
    price = 100
    for s in strategies:
        s(price)


# ============================================================
# 5. 作为装饰器使用
# ============================================================
def demo_decorator():
    class Logger:
        """一个可调用类作为装饰器"""
        def __init__(self, prefix="LOG"):
            self.prefix = prefix

        def __call__(self, func):
            """当装饰器使用时, __call__ 接收被装饰的函数"""
            def wrapper(*args, **kwargs):
                print(f"[{self.prefix}] 调用 {func.__name__}({args}, {kwargs})")
                result = func(*args, **kwargs)
                print(f"[{self.prefix}] 返回 {result}")
                return result
            return wrapper

    print("\n--- 可调用类作为装饰器 ---")

    @Logger("TEST")
    def add(a, b):
        return a + b

    add(3, 5)


# ============================================================
# 6. 检查一个对象是否可调用
# ============================================================
def demo_check_callable():
    def add(a, b):
        return a + b

    class Counter:
        def __init__(self):
            self.count = 0

        def __call__(self):
            self.count += 1
            return self.count

    counter = Counter()

    print(f"\n--- 检查是否可调用 ---")
    print(f"  函数 add: {callable(add)}")                     # True
    print(f"  类 Counter: {callable(Counter)}")               # True -- 类本身也是可调用的
    print(f"  实例 counter: {callable(counter)}")             # True -- 因为有 __call__
    print(f"  普通对象: {callable('hello')}")                  # False
    print(f"  lambda: {callable(lambda x: x)}")               # True


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "counter": demo_counter,
        "adder": demo_adder,
        "memoize": demo_memoize,
        "strategy": demo_strategy,
        "decorator": demo_decorator,
        "check_callable": demo_check_callable,
    }
    if len(sys.argv) > 1:
        fn = demos.get(sys.argv[1])
        if fn is None:
            print(f"未知案例 '{sys.argv[1]}', 可选: {', '.join(demos)}")
            sys.exit(1)
        fn()
    else:
        for fn in demos.values():
            fn()


# ============================================================
# 总结
# ============================================================
# - __call__ 让实例可以像函数一样 obj() 调用
# - 本质: 带状态 (属性)的函数
# - 典型用途: 计数器, 缓存, 策略, 装饰器, 回调
# - callable(obj) 可以判断一个对象是否可调用
# - 类也是可调用的 (调用类 = 创建实例)
