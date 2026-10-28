"""
协程基础 -- async/await 入门

[运行方式]
  全部: python 09_async_basics.py
  单个: python 09_async_basics.py basic / gather / concurrency / exception / sleep / async_for
"""

import asyncio
import time


# ============================================================
# 案例 1: 最基本的协程 -- async def + await + asyncio.run
# ============================================================
def demo_basic():
    async def greet(name):
        print(f"  开始问候 {name}")
        await asyncio.sleep(0.5)      # 非阻塞等待
        print(f"  问候 {name} 完成")
        return f"Hello, {name}"

    async def main():
        print("--- 基础: async def + await ---")
        result = await greet("Alice")
        print(f"  返回值: {result}")

    asyncio.run(main())               # 程序入口: 启动事件循环


# ============================================================
# 案例 2: gather -- 并发运行多个协程 (保序返回)
# ============================================================
def demo_gather():
    async def fetch(name, delay):
        await asyncio.sleep(delay)
        return f"{name} (耗时 {delay}s)"

    async def main():
        print("--- gather: 并发运行, 按输入顺序返回 ---")
        start = time.perf_counter()
        results = await asyncio.gather(
            fetch("A", 1),
            fetch("B", 2),
            fetch("C", 0.5),
        )
        print(f"  结果: {results}")
        print(f"  总耗时: {time.perf_counter() - start:.2f}s  (并发, 约 2s 不是 3.5s)")

    asyncio.run(main())


# ============================================================
# 案例 3: 三种并发执行方式 -- 直接 await / create_task / gather
# ============================================================
def demo_concurrency():
    async def greet(name):
        print(f"  开始问候 {name}")
        await asyncio.sleep(1)
        print(f"  问候 {name} 完成")
        return f"Hello, {name}"

    async def main():
        print("--- 方式一: 直接 await (顺序执行)---")
        start = time.perf_counter()
        await greet("Alice")
        await greet("Bob")
        print(f"  耗时: {time.perf_counter() - start:.2f}s\n")

        print("--- 方式二: create_task (并发执行, 可逐个控制)---")
        start = time.perf_counter()
        task1 = asyncio.create_task(greet("Charlie"))
        task2 = asyncio.create_task(greet("Dave"))
        r3 = await task1
        r4 = await task2
        print(f"  结果: {r3}, {r4}")
        print(f"  耗时: {time.perf_counter() - start:.2f}s\n")

        print("--- 方式三: gather (批量并发, 保序返回)---")
        start = time.perf_counter()
        results = await asyncio.gather(
            greet("Eve"),
            greet("Frank"),
        )
        print(f"  结果: {results}")
        print(f"  耗时: {time.perf_counter() - start:.2f}s")

    asyncio.run(main())


# ============================================================
# 案例 4: 异常处理 -- 默认抛出 vs return_exceptions=True
# ============================================================
def demo_exception():
    async def risky_task(name, should_fail):
        await asyncio.sleep(0.5)
        if should_fail:
            raise ValueError(f"{name} 失败了")
        return f"{name} 成功"

    async def main():
        print("--- 默认: 第一个异常时抛出 ---")
        try:
            results = await asyncio.gather(
                risky_task("A", False),
                risky_task("B", True),
            )
            print(f"  结果: {results}")
        except ValueError as e:
            print(f"  捕获异常: {e}\n")

        print("--- return_exceptions=True: 异常作为结果返回 ---")
        results = await asyncio.gather(
            risky_task("D", False),
            risky_task("E", True),
            return_exceptions=True,
        )
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                print(f"  任务 {i} 失败: {r}")
            else:
                print(f"  任务 {i} 成功: {r}")

    asyncio.run(main())


# ============================================================
# 案例 5: 阻塞 vs 非阻塞 -- time.sleep vs asyncio.sleep
# ============================================================
def demo_sleep():
    async def blocking_demo():
        print("--- 错误示范: 协程里用 time.sleep ---")
        start = time.perf_counter()
        for i in range(3):
            time.sleep(1)             # 阻塞! 卡死事件循环
            print(f"  第 {i+1} 次完成")
        print(f"  总耗时: {time.perf_counter() - start:.2f}s (串行 3s)")

    async def nonblocking_demo():
        print("--- 正确示范: 用 asyncio.sleep ---")
        start = time.perf_counter()
        await asyncio.gather(
            asyncio.sleep(1),
            asyncio.sleep(1),
            asyncio.sleep(1),
        )
        print(f"  总耗时: {time.perf_counter() - start:.2f}s (并发 1s)")

    async def main():
        await blocking_demo()
        await nonblocking_demo()

    asyncio.run(main())


# ============================================================
# 案例 6: async for / async with
# ============================================================
def demo_async_for():
    async def async_range(n):
        """一个异步迭代器: 每次 yield 前 await 一下"""
        for i in range(n):
            await asyncio.sleep(0.2)
            yield i

    class AsyncResource:
        """一个异步上下文管理器"""
        async def __aenter__(self):
            print("  打开资源")
            await asyncio.sleep(0.1)
            return self

        async def __aexit__(self, exc_type, exc, tb):
            print("  关闭资源")
            await asyncio.sleep(0.1)

    async def main():
        print("--- async for: 异步迭代 ---")
        async for i in async_range(3):
            print(f"  拿到 {i}")

        print("\n--- async with: 异步上下文管理器 ---")
        async with AsyncResource():
            print("  资源使用中...")

    asyncio.run(main())


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "basic": demo_basic,
        "gather": demo_gather,
        "concurrency": demo_concurrency,
        "exception": demo_exception,
        "sleep": demo_sleep,
        "async_for": demo_async_for,
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
# async def      → 定义协程函数
# await          → 等待协程完成, 挂起当前协程
# asyncio.run()  → 启动事件循环 (程序入口)
# create_task    → 包装成 Task, 立即调度 (可单独控制)
# asyncio.gather → 并发运行多个协程, 保序返回
# asyncio.sleep  → 非阻塞 sleep (协程版)
# async for/with → 异步迭代 / 异步上下文管理器
#
# 三种并发方式:
#   直接 await    → 顺序执行 (有依赖时用)
#   create_task  → 并发, 可单独控制 (要取消/查状态时用)
#   gather       → 批量并发, 保序返回 (最常用)
#
# 异常处理:
#   gather 默认            → 第一个异常立即抛出 (其他任务不取消)
#   return_exceptions=True → 异常作为结果返回 (适合部分失败)
#
# 铁律: 协程里绝不直接调 time.sleep() 等阻塞函数, 否则卡死事件循环