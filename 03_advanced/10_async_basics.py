"""
异步编程基础 —— async / await / asyncio

【问题场景: 为什么需要异步?】

  同步代码的问题 ── 等待 I/O 时整个程序卡住:
    def fetch(url):
        response = request(url)    # 网络请求, 等 1 秒
        return response.text       # 这 1 秒内 CPU 在发呆

    # 请求 10 个 URL, 串行执行
    for url in urls:
        data = fetch(url)          # 每个等 1 秒, 总共 10 秒

  异步代码的优势 ── 等待 I/O 时切换到其他任务:
    async def fetch(url):
        response = await request(url)   # 等的时候让出给别的任务
        return response.text

    # 请求 10 个 URL, 并发执行
    await asyncio.gather(*[fetch(url) for url in urls])  # 总共约 1 秒

【核心概念】

  ┌──────────────┬────────────────────────────────────────────┐
  │ 概念          │ 解释                                        │
  ├──────────────┼────────────────────────────────────────────┤
  │ coroutine    │ async def 定义的函数, 调用它不立即执行,      │
  │ (协程)       │ 而是返回一个协程对象                          │
  ├──────────────┼────────────────────────────────────────────┤
  │ await        │ 等待一个协程完成, 在此期间交出控制权           │
  │              │ 给事件循环去执行其他任务                      │
  ├──────────────┼────────────────────────────────────────────┤
  │ event loop   │ 事件循环 = 调度器, 负责轮流执行所有协程       │
  │ (事件循环)    │ 哪个协程在等 I/O 就先放一边, 执行别的        │
  ├──────────────┼────────────────────────────────────────────┤
  │ Task         │ 把协程包装成 Task 交给事件循环调度            │
  │              │ asyncio.create_task(coro)                   │
  ├──────────────┼────────────────────────────────────────────┤
  │ asyncio.run()│ 启动事件循环, 运行传入的协程, 返回结果        │
  │              │ 是程序进入异步世界的入口                      │
  └──────────────┴────────────────────────────────────────────┘

【异步 != 多线程 —— 最重要的一句话】

  异步是单线程内切换任务, 不是并行执行.
  适合:  I/O 密集型 (网络请求, 数据库查询, 文件读写) ── 等待时切换
  不适合: CPU 密集型 (计算, 图像处理) ── 没有"等待", 没机会切换

  打个比方:
    多线程 = 多个收银台同时工作 (并行)
    异步   = 一个收银员, 但趁顾客掏钱包时给另一个人结账 (并发)

【async/await 的特殊方法 —— 异步版本的魔术方法】

  同步版本            异步版本              用途
  ────────────────── ──────────────────── ──────────
  __iter__ / __next__  __aiter__ / __anext__  async for
  __enter__ / __exit__ __aenter__ / __aexit__  async with

  用法:
    async for item in async_iterable:   # 代替 for
        ...

    async with async_context() as res:  # 代替 with
        ...

【几个关键约束】

  1. await 只能用在 async def 函数内部
  2. 不能在普通函数里调用 await
  3. asyncio.run() 是给同步代码进入异步世界的入口函数
     (实际项目如 FastAPI 中, 框架帮你管理事件循环, 你只需写 async def)
  4. await 后面的对象必须是 "awaitable": 协程, Task, 或实现了 __await__ 的对象

【常见误区】

  误区 1: "async 函数一定比同步快"
    真相: 对单个任务, async 反而慢 (调度有开销). 优势体现在大量并发 I/O 时.

  误区 2: "await 让代码并行执行了"
    真相: await 是在等, 不是并行. 只有 gather()/create_task() 才让多个协程并发跑.

  误区 3: "asyncio.sleep() 和 time.sleep() 一样"
    真相: time.sleep() 阻塞整个线程; asyncio.sleep() 只挂起当前协程, 其他协程继续跑.

【运行方式】
  全部: python 10_async_basics.py
  单个: python 10_async_basics.py sync_vs_async / basics / async_iter / async_with / concurrent_download / producer_consumer / error_handling / run_principle
"""

import asyncio
import time

# ============================================================
# 1. 同步 vs 异步 —— 直观对比
# ============================================================
def demo_sync_vs_async():
    # 同步版本：一个个等，总时间 = 每个任务时间之和
    def sync_task(name, delay):
        """同步任务：阻塞等待"""
        print(f"  [{name}] 开始")
        time.sleep(delay)                    # 阻塞整个线程
        print(f"  [{name}] 完成 ({delay}s)")
        return f"{name} 结果"

    def run_sync():
        print("同步执行：")
        start = time.perf_counter()
        sync_task("A", 1)
        sync_task("B", 1)
        sync_task("C", 1)
        print(f"  总耗时: {time.perf_counter() - start:.2f}s")   # 约 3s

    run_sync()

    # 异步版本：等待时切换，总时间 ≈ 最长的那个任务时间
    async def async_task(name, delay):
        """异步任务：等待时不阻塞"""
        print(f"  [{name}] 开始")
        await asyncio.sleep(delay)           # 交出控制权，不阻塞
        print(f"  [{name}] 完成 ({delay}s)")
        return f"{name} 结果"

    async def run_async():
        print("\n异步执行：")
        start = time.perf_counter()
        # asyncio.gather: 并发执行多个协程
        results = await asyncio.gather(
            async_task("A", 1),
            async_task("B", 1),
            async_task("C", 1),
        )
        print(f"  总耗时: {time.perf_counter() - start:.2f}s")   # 约 1s
        print(f"  结果: {results}")

    asyncio.run(run_async())


# ============================================================
# 2. async/await 基本用法
# ============================================================
def demo_basics():
    # async def → 定义一个协程函数
    async def greet(name):
        await asyncio.sleep(0.1)         # 模拟 I/O 等待
        return f"Hello, {name}"

    # await → 等待另一个协程，交出控制权给事件循环
    async def main():
        print("\n--- async/await 基础 ---")

        # 方式一: 直接 await（顺序执行）
        r1 = await greet("Alice")
        r2 = await greet("Bob")
        print(f"  顺序: {r1}, {r2}")

        # 方式二: create_task 并发执行
        task1 = asyncio.create_task(greet("Charlie"))
        task2 = asyncio.create_task(greet("Dave"))
        r3 = await task1
        r4 = await task2
        print(f"  并发: {r3}, {r4}")

        # 方式三: asyncio.gather 批量并发
        results = await asyncio.gather(
            greet("Eve"),
            greet("Frank"),
        )
        print(f"  gather: {results}")

    asyncio.run(main())


# ============================================================
# 3. 异步迭代器 —— __aiter__ / __anext__
# ============================================================
def demo_async_iter():
    class AsyncCounter:
        """异步迭代器：每次迭代之间可以 await"""
        def __init__(self, start, end):
            self.start = start
            self.end = end

        def __aiter__(self):           # 对应同步的 __iter__
            self.current = self.start
            return self

        async def __anext__(self):     # 对应同步的 __next__
            if self.current >= self.end:
                raise StopAsyncIteration    # 对应 StopIteration
            await asyncio.sleep(0.1)        # 模拟 I/O
            value = self.current
            self.current += 1
            return value

    async def test_async_iter():
        print("\n--- 异步迭代器 ---")
        async for num in AsyncCounter(1, 4):   # async for 代替 for
            print(f"  {num}", end=" ")
        print()

    asyncio.run(test_async_iter())


# ============================================================
# 4. 异步上下文管理器 —— __aenter__ / __aexit__
# ============================================================
def demo_async_with():
    class AsyncResource:
        """异步上下文管理器"""
        async def __aenter__(self):
            print("  异步获取资源...")
            await asyncio.sleep(0.1)
            return "资源"

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            print("  异步释放资源...")
            await asyncio.sleep(0.05)

    async def test_async_with():
        print("\n--- 异步上下文管理器 ---")
        async with AsyncResource() as res:   # async with 代替 with
            print(f"  使用 {res}")
            await asyncio.sleep(0.1)

    asyncio.run(test_async_with())


# ============================================================
# 5. 实用案例：并发下载多个 URL
# ============================================================
def demo_concurrent_download():
    # 模拟网络请求
    async def fetch(url):
        """模拟 HTTP 请求"""
        print(f"  请求 {url} ...")
        await asyncio.sleep(0.5)         # 模拟网络延迟
        return f"<{url} 的内容>"

    async def fetch_all(urls):
        print("\n--- 并发请求多个 URL ---")
        start = time.perf_counter()
        tasks = [fetch(url) for url in urls]
        results = await asyncio.gather(*tasks)
        print(f"  耗时: {time.perf_counter() - start:.2f}s")
        for result in results:
            print(f"  {result}")

    asyncio.run(fetch_all([
        "http://api.example.com/users",
        "http://api.example.com/posts",
        "http://api.example.com/comments",
    ]))


# ============================================================
# 6. 生产者-消费者模式
# ============================================================
def demo_producer_consumer():
    async def producer(queue):
        """生产者：往队列里放数据"""
        for i in range(5):
            await asyncio.sleep(0.2)      # 生产需要时间
            await queue.put(f"物品{i}")
            print(f"  生产: 物品{i}")

    async def consumer(queue):
        """消费者：从队列里取数据"""
        for _ in range(5):
            item = await queue.get()
            await asyncio.sleep(0.3)      # 消费需要时间
            print(f"  消费: {item}")
            queue.task_done()

    async def run_pipeline():
        print("\n--- 生产者-消费者 ---")
        queue = asyncio.Queue()
        # 生产者和消费者并发运行
        await asyncio.gather(
            producer(queue),
            consumer(queue),
        )

    asyncio.run(run_pipeline())


# ============================================================
# 7. 异常处理
# ============================================================
def demo_error_handling():
    async def risky_task(name, should_fail):
        await asyncio.sleep(0.1)
        if should_fail:
            raise ValueError(f"{name} 失败了")
        return f"{name} 成功"

    async def test_error_handling():
        print("\n--- 异步异常处理 ---")
        # gather 默认会在第一个异常时抛出
        try:
            results = await asyncio.gather(
                risky_task("A", False),
                risky_task("B", True),        # 这个会失败
                risky_task("C", False),
            )
        except ValueError as e:
            print(f"  捕获异常: {e}")

        # return_exceptions=True: 异常作为结果返回
        results = await asyncio.gather(
            risky_task("D", False),
            risky_task("E", True),
            return_exceptions=True,
        )
        print(f"  带异常的结果: {results}")

    asyncio.run(test_error_handling())


# ============================================================
# 8. asyncio.run() 原理简述
# ============================================================
def demo_run_principle():
    """
    asyncio.run(coro) 做的事情：
      1. 创建一个事件循环 (Event Loop)
      2. 把协程包装成 Task
      3. 运行事件循环直到协程完成
      4. 关闭事件循环

    每个线程只能有一个事件循环在运行。
    asyncio.run() 是一个方便的入口，实际项目（如 FastAPI）中框架帮你管理循环。
    """


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "sync_vs_async": demo_sync_vs_async,
        "basics": demo_basics,
        "async_iter": demo_async_iter,
        "async_with": demo_async_with,
        "concurrent_download": demo_concurrent_download,
        "producer_consumer": demo_producer_consumer,
        "error_handling": demo_error_handling,
        "run_principle": demo_run_principle,
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
# async def        → 定义协程
# await            → 等待协程，交出控制权
# asyncio.run()    → 运行协程的入口
# asyncio.gather() → 并发执行多个协程
# asyncio.create_task() → 把协程包装成 Task 放入事件循环
#
# 异步版本的特殊方法:
#   __aiter__ / __anext__           → async for
#   __aenter__ / __aexit__          → async with
#
# 关键认知:
#   - 异步 ≠ 并行多线程，单线程 I/O 复用
#   - 适合: 网络请求、数据库查询、文件读写（大量 I/O 等待）
#   - 不适合: CPU 密集计算（用多进程替代）
#   - await 只能用在 async def 函数内部
