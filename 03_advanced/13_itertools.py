"""
itertools 模块 —— 高效的迭代器工具集

全部惰性求值：用到一个产一个，内存占用极低。

【运行方式】
  全部: python 13_itertools.py
  单个: python 13_itertools.py infinite / terminating / combining / grouping / slicing / pairwise / tee / use_cases
"""

import itertools
import operator
from itertools import (
    count, cycle, repeat,
    accumulate, chain, compress, dropwhile, takewhile, filterfalse,
    product, permutations, combinations, combinations_with_replacement,
    groupby, islice, pairwise, tee,
)


# ============================================================
# 1. 无限迭代器
# ============================================================
def demo_infinite():
    # count(start, step)：无限递增
    for i in count(10, 2):
        if i > 20:
            break
        print(i, end=" ")                # 10 12 14 16 18 20
    print()

    # cycle(iterable)：无限循环
    colors = cycle(["红", "绿", "蓝"])
    print([next(colors) for _ in range(7)])   # 红 绿 蓝 红 绿 蓝 红

    # repeat(obj, times)：重复；times 省略则无限
    print(list(repeat("x", 3)))          # ['x', 'x', 'x']

    # 常配合 zip：给每个元素配固定值
    print(list(zip(range(1, 4), repeat("标签"))))
    # [(1, '标签'), (2, '标签'), (3, '标签')]


# ============================================================
# 2. 终止迭代器（一）
# ============================================================
def demo_terminating_1():
    # accumulate：累积，默认求和，可传 func
    print(list(accumulate([1, 2, 3, 4, 5])))              # [1, 3, 6, 10, 15]
    print(list(accumulate([1, 2, 3, 4], operator.mul)))   # [1, 2, 6, 24]
    print(list(accumulate([3, 1, 4, 1, 5], max)))         # [3, 3, 4, 4, 5]

    # chain：串联多个可迭代对象
    print(list(chain([1, 2], [3, 4], "ab")))              # [1, 2, 3, 4, 'a', 'b']
    print(list(chain.from_iterable([[1, 2], [3, 4], [5]])))  # [1, 2, 3, 4, 5]

    # compress：按真假值筛选
    data = ["a", "b", "c", "d", "e"]
    mask = [1, 0, 1, 1, 0]
    print(list(compress(data, mask)))                     # ['a', 'c', 'd']


# ============================================================
# 3. 终止迭代器（二）
# ============================================================
def demo_terminating_2():
    nums = [1, 2, 3, 10, 1, 2]

    # dropwhile：丢弃开头满足条件的，遇到第一个不满足就停
    print(list(dropwhile(lambda x: x < 5, nums)))         # [10, 1, 2]

    # takewhile：保留开头满足条件的，遇到第一个不满足就停
    print(list(takewhile(lambda x: x < 5, nums)))         # [1, 2, 3]

    # filterfalse：逐个筛，保留 pred 为 False 的
    print(list(filterfalse(lambda x: x % 2, range(10))))  # [0, 2, 4, 6, 8]
    print(list(filter(lambda x: x % 2, range(10))))       # [1, 3, 5, 7, 9]


# ============================================================
# 4. 组合迭代器
# ============================================================
def demo_combining():
    # product：笛卡尔积（有序，可重复取同一元素）
    print(list(product("AB", "12")))
    # [('A','1'), ('A','2'), ('B','1'), ('B','2')]
    print(list(product([0, 1], repeat=2)))
    # [(0,0), (0,1), (1,0), (1,1)]

    # permutations：排列（有序，不重复取同一位置）
    print(list(permutations("ABC", 2)))
    # [('A','B'), ('A','C'), ('B','A'), ('B','C'), ('C','A'), ('C','B')]

    # combinations：组合（无序，不重复）
    print(list(combinations("ABC", 2)))
    # [('A','B'), ('A','C'), ('B','C')]

    # combinations_with_replacement：可重复组合
    print(list(combinations_with_replacement("ABC", 2)))
    # [('A','A'), ('A','B'), ('A','C'), ('B','B'), ('B','C'), ('C','C')]


# ============================================================
# 5. groupby 分组
# ============================================================
def demo_grouping():
    # 只对"相邻"元素分组，通常要先排序
    data = [
        ("水果", "苹果"), ("水果", "香蕉"),
        ("蔬菜", "白菜"), ("蔬菜", "萝卜"),
        ("水果", "橙子"),
    ]
    for key, group in groupby(data, key=lambda x: x[0]):
        print(key, list(group))
    # 水果 [两个] / 蔬菜 [两个] / 水果 [一个]  ← 分成了 3 组

    data.sort(key=lambda x: x[0])
    for key, group in groupby(data, key=lambda x: x[0]):
        print(key, list(group))
    # 水果 [三个] / 蔬菜 [两个]

    words = ["apple", "banana", "avocado", "cherry", "blueberry"]
    words.sort()
    for letter, group in groupby(words, key=lambda w: w[0]):
        print(letter, list(group))
    # a ['apple', 'avocado'] / b ['banana', 'blueberry'] / c ['cherry']


# ============================================================
# 6. islice 切片
# ============================================================
def demo_slicing():
    print(list(islice(count(), 5)))              # [0, 1, 2, 3, 4]
    print(list(islice(range(10), 2, 6)))         # [2, 3, 4, 5]
    print(list(islice(range(10), 0, 10, 3)))     # [0, 3, 6, 9]
    print(list(islice(cycle("AB"), 7)))          # ['A','B','A','B','A','B','A']
    print(list(islice(count(100), 3)))           # [100, 101, 102]


# ============================================================
# 7. pairwise 相邻配对（Python 3.10+）
# ============================================================
def demo_pairwise():
    print(list(pairwise([1, 2, 3, 4, 5])))       # [(1,2), (2,3), (3,4), (4,5)]

    nums = [10, 13, 15, 20]
    print([b - a for a, b in pairwise(nums)])    # [3, 2, 5]

    nums2 = [1, 3, 5, 7]
    print(all(a < b for a, b in pairwise(nums2)))  # True


# ============================================================
# 8. tee 复制迭代器
# ============================================================
def demo_tee():
    original = iter([1, 2, 3, 4])
    a, b = tee(original, 2)
    print(list(a))                               # [1, 2, 3, 4]
    print(list(b))                               # [1, 2, 3, 4]

    it = iter([1, 2, 3])
    print(list(it))                              # [1, 2, 3]
    print(list(it))                              # []  ← 不复制就空了


# ============================================================
# 9. 迭代器是消耗品
# ============================================================
def demo_consumable():
    it = iter([1, 2, 3])
    print(list(it))                              # [1, 2, 3]
    print(list(it))                              # []

    g = (x * 2 for x in range(3))
    print(list(g))                               # [0, 2, 4]
    print(list(g))                               # []


# ============================================================
# 10. 实际应用案例
# ============================================================
def demo_use_cases():
    # 案例 1：所有密码组合
    for length in range(1, 3):
        for combo in product("ab", repeat=length):
            print("".join(combo), end=" ")       # a b aa ab ba bb
    print()

    # 案例 2：滑动窗口（tee 错位 + zip）
    def sliding_window(iterable, n):
        iters = tee(iterable, n)
        for i, it in enumerate(iters):
            for _ in range(i):
                next(it, None)
        return zip(*iters)

    print(list(sliding_window([1, 2, 3, 4, 5], 3)))
    # [(1,2,3), (2,3,4), (3,4,5)]

    # 案例 3：流水线（chain + takewhile + accumulate）
    pipeline = accumulate(
        takewhile(lambda x: x < 7, chain([1, 2, 3], [4, 5, 6, 7, 8]))
    )
    print(list(pipeline))                        # [1, 3, 6, 10, 15, 21]

    # 案例 4：按长度分组单词
    words = ["a", "bb", "cc", "ddd", "ee", "f"]
    words.sort(key=len)
    for length, group in groupby(words, key=len):
        print(f"长度 {length}: {list(group)}")


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "infinite": demo_infinite,
        "terminating": demo_terminating_1,
        "terminating2": demo_terminating_2,
        "combining": demo_combining,
        "grouping": demo_grouping,
        "slicing": demo_slicing,
        "pairwise": demo_pairwise,
        "tee": demo_tee,
        "consumable": demo_consumable,
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
# 无限:    count / cycle / repeat
# 终止:    accumulate / chain / compress
#          dropwhile / takewhile / filterfalse
# 组合:    product / permutations / combinations / combinations_with_replacement
# 其他:    groupby / islice / pairwise / tee
#
# 关键点:
#   - 全部惰性，按需产出
#   - 迭代器是消耗品，遍历一次就空
#   - groupby 只对相邻元素分组，先 sort 再 group
#   - islice 可对无限序列切片
#   - 组合区别：
#       product                       有序，可重复
#       permutations                  有序，不重复
#       combinations                  无序，不重复
#       combinations_with_replacement 无序，可重复