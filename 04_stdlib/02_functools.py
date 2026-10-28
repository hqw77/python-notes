"""
functools 模块 —— 函数工具箱

【问题场景: 三种每天都要手写一遍的样板代码】

  1) 同一个函数被反复调用，参数相同结果也相同，想缓存：
        cache = {}
        if key in cache:
            return cache[key]
        cache[key] = slow_fn(key)
        return cache[key]
     → lru_cache / cache：一个装饰器搞定，还自动做 LRU 淘汰。

  2) 想给函数固定几个参数：
        def power2(x):
            return power(x, 2)        # 只为固定一个参数，多写一个函数
     → partial：partial(power, exp=2)，不用新写函数。

  3) 自己写了装饰器，结果被装饰函数的 __name__ 变成了 wrapper：
     → wraps：把原函数的元信息原样搬过去。

【核心概念】

  ┌────────────────────┬────────────────────────────────────────────┐
  │ lru_cache / cache  │ 记忆化缓存：同一组参数只算一次              │
  │ cached_property    │ 属性级缓存：每个实例只算一次                │
  │ partial            │ 固定部分参数，生成新函数                    │
  │ partialmethod      │ 同上，但用于类的方法                        │
  │ reduce             │ 归约：把二元函数累积作用到整个序列          │
  │ wraps              │ 装饰器里保留原函数的元信息                  │
  │ singledispatch     │ 按第一个参数的类型分发到不同实现            │
  │ total_ordering     │ 只写 __eq__ + __lt__，其余比较自动补齐      │
  │ cmp_to_key         │ 旧式比较函数转成排序 key                    │
  └────────────────────┴────────────────────────────────────────────┘

【运行方式】
  全部: python 02_functools.py
  单个: python 02_functools.py reduce / partial / lru_cache / cached_property / wraps / singledispatch / total_ordering / cmp_to_key / use_cases
"""

import time
from functools import (
    reduce, partial, lru_cache, cache, cached_property,
    wraps, singledispatch, total_ordering, cmp_to_key,
)


# ============================================================
# 1. reduce —— 归约
# ============================================================
def demo_reduce():
    print("--- 1. reduce: 把二元函数累积作用到序列上 ---")

    nums = [1, 2, 3, 4, 5]
    print(f"  reduce(add, {nums}) = {reduce(lambda a, b: a + b, nums)}")
    print(f"  等价于: 1+2+3+4+5 = {sum(nums)}")
    print(f"  带初始值 10: {reduce(lambda a, b: a + b, nums, 10)}")
    print(f"  求最大值: {reduce(lambda a, b: a if a > b else b, nums)}   (内置 max 更直接)")

    nested = [[1, 2], [3, 4], [5]]
    print(f"  拍平 {nested}: {reduce(lambda acc, x: acc + x, nested, [])}")

    print("  提示: 能用 sum / max / any / all 就别用 reduce，可读性更好")


# ============================================================
# 2. partial —— 偏函数
# ============================================================
def demo_partial():
    print("--- 2. partial: 固定部分参数 ---")

    int2 = partial(int, base=2)          # 二进制解析器
    print(f"  int2('1010') = {int2('1010')}   <- partial(int, base=2)")
    print(f"  临时覆盖关键字: int2('1010', base=10) = {int2('1010', base=10)}")

    def power(base, exp):
        return base ** exp

    square = partial(power, exp=2)
    cube = partial(power, exp=3)
    print(f"  square(5) = {square(5)}, cube(2) = {cube(2)}")

    # 位置参数也能固定
    def greet(greeting, name):
        return f"{greeting}, {name}!"

    hello = partial(greet, "Hello")
    print(f"  hello('World') = {hello('World')}")

    print(f"  partial 保留了原函数信息: .func={square.func.__name__}, .keywords={square.keywords}")
    print("  和 lambda 的区别: partial 可读、可复用、能看出原函数；lambda 一长就糊")


# ============================================================
# 3. lru_cache / cache —— 记忆化
# ============================================================
def demo_lru_cache():
    print("--- 3. lru_cache: 同一组参数只算一次 ---")

    @lru_cache(maxsize=None)
    def fib_cached(n):
        return n if n < 2 else fib_cached(n - 1) + fib_cached(n - 2)

    def fib_plain(n):
        return n if n < 2 else fib_plain(n - 1) + fib_plain(n - 2)

    n = 28
    t0 = time.perf_counter()
    r1 = fib_plain(n)
    t_plain = time.perf_counter() - t0

    t0 = time.perf_counter()
    r2 = fib_cached(n)
    t_cached = time.perf_counter() - t0

    print(f"  fib({n}) 不用缓存: {r1}, 耗时 {t_plain * 1000:.1f}ms")
    print(f"  fib({n}) 用缓存  : {r2}, 耗时 {t_cached * 1000:.3f}ms")
    print(f"  加速: {t_plain / max(t_cached, 1e-9):.0f} 倍")
    print(f"  cache_info: {fib_cached.cache_info()}")

    fib_cached.cache_clear()
    print(f"  cache_clear 之后: {fib_cached.cache_info()}")

    # maxsize 控制缓存条目数，超出按 LRU 淘汰
    @lru_cache(maxsize=2)
    def square(x):
        print(f"    [真正计算 {x}]")
        return x * x

    print("  maxsize=2，依次调用 square(1) / (2) / (3) / (1)：")
    for i in [1, 2, 3, 1]:
        square(i)
    print(f"  cache_info: {square.cache_info()}   <- 第 4 次调用 (1) 被淘汰，重算了")

    # cache 就是 maxsize=None 的简写 (3.9+)
    @cache
    def slow_add(a, b):
        time.sleep(0.01)
        return a + b

    slow_add(1, 2)
    t0 = time.perf_counter()
    slow_add(1, 2)
    print(f"  @cache 第二次调用耗时 {time.perf_counter() - t0:.6f}s   <- 直接命中")

    print("  注意: 参数必须可哈希；返回可变对象时小心被外部改掉")


# ============================================================
# 4. cached_property —— 属性级缓存
# ============================================================
def demo_cached_property():
    print("--- 4. cached_property: 每个实例只算一次 ---")

    class WithCache:
        def __init__(self, data):
            self.data = data
            self.computed = 0

        @cached_property
        def summary(self):
            self.computed += 1
            return {"count": len(self.data), "sum": sum(self.data)}

    class WithProperty:
        def __init__(self, data):
            self.data = data
            self.computed = 0

        @property
        def summary(self):
            self.computed += 1
            return {"count": len(self.data), "sum": sum(self.data)}

    a, b = WithCache([1, 2, 3]), WithProperty([1, 2, 3])
    _ = a.summary
    _ = a.summary
    _ = b.summary
    _ = b.summary
    print(f"  cached_property 访问两次，实际计算 {a.computed} 次")
    print(f"  @property       访问两次，实际计算 {b.computed} 次")

    # 结果缓存在实例 __dict__ 里，可以直接覆盖
    a.__dict__["summary"] = {"count": 0, "sum": 0}
    print(f"  可以手动覆盖缓存: {a.summary}")

    print("  适用: 计算一次很贵、之后只读的派生属性（如统计、序列化结果）")


# ============================================================
# 5. wraps —— 装饰器保留元信息
# ============================================================
def demo_wraps():
    print("--- 5. wraps: 别让装饰器吃掉函数身份 ---")

    def timer_bad(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    def timer_good(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @timer_bad
    def add_bad(x, y):
        """两数相加"""
        return x + y

    @timer_good
    def add_good(x, y):
        """两数相加"""
        return x + y

    print(f"  不加 wraps: __name__={add_bad.__name__!r}, __doc__={add_bad.__doc__!r}")
    print(f"  加了 wraps: __name__={add_good.__name__!r}, __doc__={add_good.__doc__!r}")
    print("  影响: 调试栈、help()、pytest 的用例名、FastAPI 的路由名都看 __name__")


# ============================================================
# 6. singledispatch —— 按类型分发
# ============================================================
def demo_singledispatch():
    print("--- 6. singledispatch: 按第一个参数的类型分发 ---")

    @singledispatch
    def show(obj):
        return f"未知类型 {type(obj).__name__}"

    @show.register(int)
    def _(obj):
        return f"整数 {obj}"

    @show.register(str)
    def _(obj):
        return f"字符串 {obj!r}，长度 {len(obj)}"

    @show.register(list)
    def _(obj):
        return f"列表，{len(obj)} 个元素"

    @show.register(float)
    def _(obj):
        return f"浮点数 {obj:.2f}"

    for value in [1, "hi", [1, 2, 3], 3.14159, {"a": 1}]:
        print(f"  {value!r:>16} -> {show(value)}")

    print("  适用: 一个函数对不同类型有不同实现，省掉一长串 isinstance 分支")


# ============================================================
# 7. total_ordering —— 少写四个比较方法
# ============================================================
def demo_total_ordering():
    print("--- 7. total_ordering: 只写 __eq__ + __lt__ ---")

    @total_ordering
    class Version:
        def __init__(self, text):
            self.parts = tuple(int(x) for x in text.split("."))

        def __eq__(self, other):
            return self.parts == other.parts

        def __lt__(self, other):
            return self.parts < other.parts

        def __repr__(self):
            return "v" + ".".join(str(x) for x in self.parts)

    versions = [Version("1.10.0"), Version("1.2.3"), Version("1.9.9")]
    print(f"  排序: {sorted(versions)}")
    print(f"  v1.10.0 > v1.2.3 ? {Version('1.10.0') > Version('1.2.3')}   <- 没写 __gt__")
    print(f"  v1.2.3 <= v1.9.9 ? {Version('1.2.3') <= Version('1.9.9')}   <- 没写 __le__")

    print("  注意: 版本号要按元组 (1,10,0) 比，不能按字符串 '1.10' < '1.2'")


# ============================================================
# 8. cmp_to_key —— 旧式比较函数转 key
# ============================================================
def demo_cmp_to_key():
    print("--- 8. cmp_to_key: 兼容旧式比较函数 ---")

    def cmp_by_abs_then_value(a, b):
        """先比绝对值，绝对值相同再比原值"""
        if abs(a) != abs(b):
            return -1 if abs(a) < abs(b) else 1
        return (a > b) - (a < b)

    nums = [-5, 3, -1, 5, 1, -3]
    print(f"  原序列: {nums}")
    print(f"  按 |x| 排序，同值负数在前: {sorted(nums, key=cmp_to_key(cmp_by_abs_then_value))}")

    print("  现在多数场景直接写 key= 就够，cmp_to_key 主要用来复用老代码里的比较函数")


# ============================================================
# 9. 实战：带缓存的查询接口
# ============================================================
def demo_use_cases():
    print("--- 9. 实战: 三个工具配合做一个带缓存的查询接口 ---")

    hits = {"db": 0}

    def log_call(func):
        """装饰器：打印每次真正发生的查询（wraps 保住原函数身份）"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"    [查库] uid={args[0]}")
            return func(*args, **kwargs)
        return wrapper

    @lru_cache(maxsize=128)
    @log_call
    def get_user(uid):
        """按 uid 取用户（模拟一次昂贵查询）"""
        hits["db"] += 1
        return {"id": uid, "name": f"user{uid}"}

    @total_ordering
    class UserScore:
        def __init__(self, uid, score):
            self.uid, self.score = uid, score

        def __eq__(self, other):
            return self.score == other.score

        def __lt__(self, other):
            return self.score < other.score

    for uid in [1, 2, 1, 3, 1]:
        get_user(uid)

    print(f"  5 次调用，实际查库 {hits['db']} 次")
    print(f"  缓存状态: {get_user.cache_info()}")
    print(f"  装饰后函数名仍是: {get_user.__name__!r}   <- wraps 的功劳")

    scores = [UserScore(1, 88), UserScore(2, 95), UserScore(3, 72)]
    print(f"  按分数排序: {[(u.uid, u.score) for u in sorted(scores, reverse=True)]}")
    print("  分工: lru_cache 省重复计算，wraps 保住函数身份，total_ordering 省比较方法")


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "reduce": demo_reduce,
        "partial": demo_partial,
        "lru_cache": demo_lru_cache,
        "cached_property": demo_cached_property,
        "wraps": demo_wraps,
        "singledispatch": demo_singledispatch,
        "total_ordering": demo_total_ordering,
        "cmp_to_key": demo_cmp_to_key,
        "use_cases": demo_use_cases,
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
# 缓存三件套:
#   lru_cache(maxsize=N)  函数级缓存，按 LRU 淘汰，参数必须可哈希
#   cache                 等于 lru_cache(maxsize=None)，3.9+
#   cached_property       属性级缓存，结果存在实例 __dict__
#
# 参数三件套:
#   partial(fn, ...)      固定部分参数生成新函数
#   partialmethod         用在类的方法上（本文件未展开，写法同理）
#   cmp_to_key            旧式比较函数 -> 排序 key
#
# 装饰器配套:
#   wraps(func)           保留 __name__ / __doc__ / __wrapped__
#
# 其它:
#   reduce                能用 sum/max 就别用
#   singledispatch        按类型分发，替代 isinstance 长链
#   total_ordering        写 __eq__ + __lt__ 自动补齐四个比较
#
# 三个坑:
#   1. lru_cache 会把参数和返回值一直留在内存里，别缓存大对象/无限参数
#   2. 缓存了可变对象，外部改了它，缓存里也跟着变
#   3. lru_cache 的 key 由参数共同决定，list/dict 参数直接报 unhashable
