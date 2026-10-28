"""
迭代器 (Iterator)

迭代器是一个可以记住遍历位置的对象, 它从第一个元素开始访问,
直到所有元素被访问完. 迭代器只能往前不会后退.

核心概念:
- 可迭代对象 (Iterable): 实现了 __iter__ 方法的对象, 可以被 iter() 调用
- 迭代器 (Iterator): 同时实现了 __iter__ 和 __next__ 方法的对象
- 迭代器一定是可迭代对象, 但可迭代对象不一定是迭代器

[运行方式]
  全部: python 11_iterator.py
  单个: python 11_iterator.py protocol / stopiteration / iterable_vs_iterator / builtin / generator / tips / type_check
"""

from collections.abc import Iterable, Iterator

# ============================================================
# 1. 迭代器协议: __iter__ 和 __next__
# ============================================================
def demo_protocol():
    class MyNumber:
        """自定义迭代器: 生成从 1 开始的连续整数"""
        def __iter__(self):
            self.a = 1
            return self          # __iter__ 必须返回迭代器对象 (通常是 self)

        def __next__(self):
            x = self.a
            self.a += 1
            return x             # __next__ 返回下一个元素

    myclass = MyNumber()
    myiter = iter(myclass)       # iter() 调用 __iter__

    print(next(myiter))          # 1, next() 调用 __next__
    print(next(myiter))          # 2
    print(next(myiter))          # 3
    print(next(myiter))          # 4
    print(next(myiter))          # 5


# ============================================================
# 2. StopIteration -- 迭代终止的信号
# ============================================================
def demo_stopiteration():
    class CountDown:
        """带终止条件的倒计时迭代器"""
        def __init__(self, start):
            self.current = start

        def __iter__(self):
            return self

        def __next__(self):
            if self.current < 0:
                raise StopIteration   # 抛出 StopIteration 表示迭代结束
            value = self.current
            self.current -= 1
            return value

    print("\n倒计时: ", end=" ")
    for num in CountDown(5):
        print(num, end=" ")           # 5 4 3 2 1 0
    print()

    # for 循环的本质:
    #   1. 调用 iter(obj) 获取迭代器
    #   2. 反复调用 next() 获取下一个值
    #   3. 捕获 StopIteration 异常, 结束循环


# ============================================================
# 3. 可迭代对象 vs 迭代器 -- 重要区别
# ============================================================
def demo_iterable_vs_iterator():
    # 可迭代对象: 有 __iter__, 每次调用 iter() 返回一个新的迭代器
    class MyList:
        def __init__(self, *items):
            self.items = list(items)

        def __iter__(self):
            return MyListIterator(self.items)  # 每次返回新迭代器, 可以多次遍历

    class MyListIterator:
        def __init__(self, items):
            self.items = items
            self.index = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self.index >= len(self.items):
                raise StopIteration
            value = self.items[self.index]
            self.index += 1
            return value

    ml = MyList(1, 2, 3)
    print("\n第一轮遍历: ", [x for x in ml])   # [1, 2, 3]
    print("第二轮遍历: ", [x for x in ml])     # [1, 2, 3] -- 可重复遍历

    # 迭代器本身: 只能遍历一次
    # nums = MyNumber()
    # print("第一次: ", list(next(nums) for _ in range(3)))  # [1, 2, 3]
    # print("继续取: ", [next(nums) for _ in range(2)])      # [4, 5] -- 状态延续, 不能重置


# ============================================================
# 4. 内置迭代器
# ============================================================
def demo_builtin():
    print("\n--- 内置迭代器 ---")

    # list, tuple, dict, set, str 都是可迭代对象, 但不是迭代器
    lst = [1, 2, 3]
    print(isinstance(lst, list))        # True -- 是 list
    # 判断是否是迭代器要用 iter(lst) 返回的对象

    it = iter(lst)
    print(type(it))                     # <class 'list_iterator'>

    # dict 的迭代
    d = {"a": 1, "b": 2, "c": 3}
    print("dict keys:", list(d.keys()))          # ['a', 'b', 'c']
    print("dict values:", list(d.values()))      # [1, 2, 3]
    print("dict items:", list(d.items()))        # [('a', 1), ('b', 2), ('c', 3)]
    print("默认迭代 dict 得到 keys:", list(d))    # ['a', 'b', 'c']

    # enumerate -- 带索引的迭代
    for i, val in enumerate(["a", "b", "c"]):
        print(f"  enumerate: [{i}]={val}", end="; ")
    print()

    # zip -- 并行迭代多个序列
    for a, b in zip([1, 2, 3], ["a", "b", "c"]):
        print(f"  zip: ({a}, {b})", end="; ")
    print()

    # reversed -- 反向迭代
    for x in reversed([1, 2, 3]):
        print(f"  reversed: {x}", end="; ")
    print()


# ============================================================
# 5. 使用生成器创建迭代器 (最常用的方式)
# ============================================================
def demo_generator():
    # 生成器函数 -- 用 yield 代替 return
    def fibonacci(n):
        """生成前 n 个斐波那契数"""
        a, b = 0, 1
        for _ in range(n):
            yield a
            a, b = b, a + b

    print("\n斐波那契:", list(fibonacci(10)))
    # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

    # 生成器表达式 -- 类似列表推导式, 用 () 而不是 []
    gen = (x ** 2 for x in range(5))
    print("生成器表达式:", list(gen))    # [0, 1, 4, 9, 16]


# ============================================================
# 6. 实用技巧
# ============================================================
def demo_tips():
    # iter() 的第二种用法: iter(callable, sentinel)
    # 反复调用 callable, 直到返回值等于 sentinel 时停止
    print("iter(callable, sentinel) 用法:")
    # 反复调用 callable, 直到返回值等于 sentinel 时停止
    # 例如: iter(lambda: input(), "")  按行读取用户输入直到空行
    # 例如: iter(f.read, "")          按块读取文件直到空字节


    # 手动取迭代器元素, 带默认值
    it = iter([10, 20, 30])
    print(next(it, "没了"))   # 10
    print(next(it, "没了"))   # 20
    print(next(it, "没了"))   # 30
    print(next(it, "没了"))   # 没了 -- 不会抛 StopIteration


# ============================================================
# 7. 检查对象是否可迭代 / 是否是迭代器
# ============================================================
def demo_type_check():
    print("\n类型检查:")
    print("list 是可迭代对象:", isinstance([1, 2, 3], Iterable))    # True
    print("list 是迭代器:", isinstance([1, 2, 3], Iterator))       # False
    print("生成器是迭代器:", isinstance((x for x in range(3)), Iterator))  # True
    print("iter(list) 是迭代器:", isinstance(iter([1, 2, 3]), Iterator))  # True


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "protocol": demo_protocol,
        "stopiteration": demo_stopiteration,
        "iterable_vs_iterator": demo_iterable_vs_iterator,
        "builtin": demo_builtin,
        "generator": demo_generator,
        "tips": demo_tips,
        "type_check": demo_type_check,
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
# 8. 总结
# ============================================================
# - 迭代器协议: __iter__ 返回自身, __next__ 返回下一个元素
# - 迭代结束: 抛出 StopIteration
# - 可迭代对象: 有 __iter__, 可以多次遍历
# - 迭代器: 有 __iter__ + __next__, 只能遍历一次
# - 生成器: 最便捷的创建迭代器的方式 (yield)
# - 内置工具: iter(), next(), enumerate(), zip(), reversed()
# - for 循环的本质: 获取迭代器 → 不断 next() → 捕获 StopIteration
