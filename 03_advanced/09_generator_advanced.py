"""
生成器进阶 —— yield from / send() / throw() / close()

【回顾: 生成器的本质】

  生成器是一种特殊的迭代器. 它的核心是: 能暂停, 能恢复.
  每次 yield 时, 函数的状态 (局部变量, 指令指针) 被冻结保存,
  下次 next() 时从冻结点继续执行.

  普通函数: 一口气跑完
  生成器:   跑一段 → 暂停 → 跑一段 → 暂停 → ... → 结束

【yield from —— 不仅仅是"省了一个 for 循环"】

  yield from 做三件事:

  1. 自动迭代:  yield from iterable  ≈ for x in iterable: yield x
  2. 双向通道:  调用方的 send(), throw(), close() 会透传给子生成器
  3. 捕获返回值: 子生成器 return 的值会被 yield from 捕获
                 (yield from 表达式的值 = 子生成器的 return 值)

  所以 yield from 本质是"把控制权完整委托给另一个生成器",
  不仅仅是省 for 循环那么简单.

【send() —— 生成器的双向通信】

  基础用法 (只产出):  yield value         → next(gen) 拿到 value
  进阶用法 (收发):    received = yield    → gen.send(data) 把 data 传入

  send() 的执行流程:
    1. 恢复生成器的执行
    2. 把 send 的参数作为上次 yield 表达式的值
    3. 生成器继续跑到下一个 yield
    4. 返回 yield 后面的值

  注意: 不能用 send() 启动一个刚创建的生成器! 必须先 next() 或 send(None)
  让生成器跑到第一个 yield 位置.

【yield 作为表达式的理解方式】

  yield 既可以"产出"，也可以"接收":

    output = yield input
    ^^^^^^        ^^^^^
    接收 send 的值  产出给 next/send 的调用方

  方向:
    调用方 ──send(value)──→ yield (接收)
    调用方 ←──yield value── yield (产出)

【三种异常控制】

  gen.throw(Type, value, tb):
    在生成器的暂停点抛入一个异常.
    生成器内部可以用 try/except 捕获并处理.

  gen.close():
    在生成器的暂停点抛入 GeneratorExit 异常.
    生成器通常无法捕获这个异常 (因为 GeneratorExit 继承自 BaseException 而非 Exception),
    但可以写在 finally 里做清理. close 让你从外部"优雅关闭"一个生成器.

  StopIteration:
    生成器 return (或自然结束) 时自动抛出, 携带 return 的值.
    yield from 会捕获这个值作为自身的返回值.

【生成器的三大优势】

  1. 惰性计算 (Lazy): 需要时才生产, 内存友好
     列表: 一次生成 100 万个元素 → 内存爆炸
     生成器: 每次只生产一个 → 内存几乎为 0

  2. 流水线 (Pipeline): 像 Unix 管道一样串联处理步骤
     reader → parser → grouper
     每个阶段都是生成器, 数据像流水线一样通过

  3. 协程 (Coroutine): send/throw/close 实现双向通信
     yield from 可以建立完整的协程调用栈

【生成器表达式 vs 列表推导式】

  列表推导式: [x**2 for x in range(N)]  → 立刻生成所有元素, 占内存
  生成器表达式: (x**2 for x in range(N)) → 惰性生成, 几乎不占内存

  什么时候用哪个?
    - 需要多次遍历, 随机访问 → 列表
    - 只需要遍历一次, 或数据很大 → 生成器
"""

# ============================================================
# 1. yield from —— 委托给子生成器
# ============================================================
# 不用 yield from: 手动迭代子生成器
def flatten_manual(nested):
    """展开嵌套列表（手动版）"""
    for sublist in nested:
        for item in sublist:
            yield item

# 用 yield from: 把迭代委托出去
def flatten_yieldfrom(nested):
    """展开嵌套列表（yield from 版）"""
    for sublist in nested:
        yield from sublist     # 等价于 for x in sublist: yield x，但更高效

print("--- yield from ---")
nested = [[1, 2], [3, 4], [5, 6]]
print(f"  手动版: {list(flatten_manual(nested))}")
print(f"  yield from 版: {list(flatten_yieldfrom(nested))}")

# yield from 的真正威力：可以委托给任何可迭代对象（生成器、列表、迭代器）
def chain(*iterables):
    """把多个可迭代对象串在一起（类似 itertools.chain）"""
    for it in iterables:
        yield from it

print(f"  串联: {list(chain('AB', 'CD', [1, 2]))}")   # ['A', 'B', 'C', 'D', 1, 2]


# ============================================================
# 2. yield from 的完整功能 —— 双向通道
# ============================================================
# yield from 不只是"自动 for 循环"，它建立了一个双向通道：
#   调用方的 send()/throw()/close() 会透传给子生成器

def sub_generator():
    """子生成器：接收值并处理"""
    total = 0
    while True:
        received = yield                    # yield 右边没有值，接收 send 传来的值
        if received is None:
            break
        print(f"    子生成器收到: {received}")
        total += received
    return total                            # return 的值会被 yield from 捕获！

def delegator():
    """委托生成器：用 yield from 委托给子生成器"""
    print("  委托开始")
    result = yield from sub_generator()     # yield from 会捕获子生成器的 return 值
    print(f"  委托结束，子生成器返回: {result}")
    yield result

print("\n--- yield from 双向通道 ---")
d = delegator()
next(d)                          # 启动，执行到子生成器的 yield
d.send(10)
d.send(20)
d.send(30)
try:
    d.send(None)                 # 发送 None 让子生成器 break
except StopIteration as e:
    print(f"  最终结果: {e.value}")


# ============================================================
# 3. send() —— 向生成器发送值（协程基础）
# ============================================================
def accumulator():
    """累加器 —— 每次 send 一个值，内部累加"""
    total = 0
    while True:
        value = yield total      # 先 yield 当前 total，然后接收 send 来的值
        if value is None:
            continue
        total += value

print("\n--- send() 发送值 ---")
acc = accumulator()
print(f"  启动: {next(acc)}")            # 必须先 next() 启动，执行到 yield，返回 0
print(f"  send(5): {acc.send(5)}")       # 发送 5，累加后返回 5
print(f"  send(10): {acc.send(10)}")     # 发送 10，累加后返回 15
print(f"  send(3): {acc.send(3)}")       # 发送 3，累加后返回 18

# send() 的本质：
#   yield 是一个表达式，可以接收值
#   value = yield output
#   ↑         ↑
#   接收值    产出值


# ============================================================
# 4. 协程流水线 —— 生成器的实际应用
# ============================================================
def reader(filename):
    """读取文件，逐行 send 给下游"""
    lines = [
        "apple 3",
        "banana 5",
        "apple 2",
        "orange 7",
        "banana 1",
    ]
    for line in lines:
        yield line

def parser(lines):
    """解析行，输出 (key, value) 元组"""
    for line in lines:
        fruit, count = line.split()
        yield fruit, int(count)

def grouper(parsed):
    """按 key 分组聚合"""
    result = {}
    for fruit, count in parsed:
        result[fruit] = result.get(fruit, 0) + count
    yield result

print("\n--- 生成器流水线 ---")
# 像管道一样串联
pipeline = grouper(parser(reader("data.txt")))
print(f"  流水线结果: {next(pipeline)}")

# 等价于手写：
# result = {}
# for fruit, count in parser(reader("data.txt")):
#     result[fruit] = result.get(fruit, 0) + count
# 但生成器版本的好处是：可以处理无限数据、内存友好


# ============================================================
# 5. throw() —— 向生成器内部抛异常
# ============================================================
def exception_handler():
    """展示生成器如何处理异常"""
    try:
        while True:
            try:
                x = yield
                print(f"    收到: {x}")
            except ValueError as e:
                print(f"    捕获 ValueError: {e}")
    finally:
        print("    生成器清理中...")

print("\n--- throw() 抛异常 ---")
gen = exception_handler()
next(gen)
gen.send("正常数据")
gen.throw(ValueError, "模拟错误")    # 向生成器内部抛异常，生成器可以捕获
gen.send("继续工作")                # 生成器还活着！


# ============================================================
# 6. close() —— 关闭生成器
# ============================================================
def closeable_gen():
    try:
        for i in range(5):
            yield i
    finally:
        print("  生成器被关闭，清理资源")

print("\n--- close() 关闭 ---")
gen = closeable_gen()
print(f"  next: {next(gen)}")    # 0
gen.close()                      # 在 yield 处抛出 GeneratorExit，触发 finally
# 之后再调用 gen 会抛 StopIteration


# ============================================================
# 7. 生成器表达式 vs 列表推导式
# ============================================================
import sys

# 列表推导式：一次性生成所有元素，占用内存
list_comp = [x ** 2 for x in range(1000000)]
# 生成器表达式：惰性生成，几乎不占内存
gen_expr = (x ** 2 for x in range(1000000))

# 比较内存占用
print(f"\n--- 内存对比 ---")
print(f"  列表推导式: {sys.getsizeof(list_comp)} 字节 (不包含元素)")
print(f"  生成器表达式: {sys.getsizeof(gen_expr)} 字节")
# 列表的 1M 个元素存在内存中，生成器只是"知道怎么算"


# ============================================================
# 总结
# ============================================================
# yield from iterable : 委托迭代，双向通道（send/throw/close 都能透传）
# send(value)          : 向生成器发送值，yield 作为表达式接收
# throw(type, val, tb) : 向生成器内部抛异常
# close()              : 关闭生成器（内部抛 GeneratorExit）
# return xxx           : 生成器返回值，被 yield from 捕获（StopIteration.value）
#
# 生成器三大优势:
#   1. 惰性计算 — 需要时才生产，内存友好
#   2. 流水线 — 像 Unix 管道一样串联处理步骤
#   3. 协程 — send/throw/close 可以实现双向通信
