"""
协程进阶 —— asyncio 生态 + 与线程/进程混用

【运行方式】
  全部: python 10_coroutine_deep.py
  单个: python 10_coroutine_deep.py completed / timeout / to_thread / bug / executor
"""

import asyncio
import time


# ============================================================
# 案例 1: asyncio.as_completed —— 谁先完成先处理
# ============================================================
def demo_completed():
    async def fetch(name, delay):
        await asyncio.sleep(delay)
        return f"{name} (耗时 {delay}s)"

    async def run():
        print("--- asyncio.as_completed: 谁先完成先打印 ---")
        tasks = [fetch("A", 2), fetch("B", 0.5), fetch("C", 1)]
        for coro in asyncio.as_completed(tasks):
            result = await coro
            print(f"  先完成的: {result}")

    asyncio.run(run())


# ============================================================
# 案例 2: 超时控制
# ============================================================
def demo_timeout():
    async def slow_task():
        await asyncio.sleep(10)
        return "太慢了"

    async def run():
        print("--- 超时控制 ---")
        try:
            async with asyncio.timeout(1):
                result = await slow_task()
                print(f"  完成: {result}")
        except TimeoutError:
            print("  超时了! 任务没在 1 秒内完成")

    asyncio.run(run())


# ============================================================
# 案例 3: 协程里调用阻塞函数 —— asyncio.to_thread
# ============================================================
def blocking_io(n):
    """一个"阻塞"函数 (比如 requests.get / 慢速文件读取)"""
    time.sleep(1)
    return f"阻塞操作 {n} 完成"

def demo_to_thread():
    async def run():
        print("--- asyncio.to_thread: 阻塞函数丢线程池, 不卡事件循环 ---")
        start = time.perf_counter()
        results = await asyncio.gather(
            asyncio.to_thread(blocking_io, 1),
            asyncio.to_thread(blocking_io, 2),
            asyncio.to_thread(blocking_io, 3),
        )
        print(f"  {results}")
        print(f"  总耗时: {time.perf_counter() - start:.2f}s  (3 个阻塞任务并发, 约 1s)")

    asyncio.run(run())


# ============================================================
# 案例 4: 错误示范 —— 在协程里直接调阻塞函数
# ============================================================
def demo_bug():
    async def run():
        print("--- 错误示范: 在协程里直接 time.sleep ---")
        start = time.perf_counter()
        for i in range(3):
            blocking_io(i)      # 直接调用, 每次卡 1 秒 (阻塞整个事件循环)
        print(f"  串行耗时: {time.perf_counter() - start:.2f}s  (3 秒, 事件循环被卡)")
        print("  对比案例 3 的 to_thread 并发版本, 差距明显")

    asyncio.run(run())


# ============================================================
# 案例 5: run_in_executor —— 协程里跑 CPU 密集 (用进程池)
# ============================================================
def cpu_heavy(x):
    total = 0
    for i in range(x):
        total += i
    return total

def demo_executor():
    async def run():
        print("--- run_in_executor: 协程里跑 CPU 密集 (用进程池) ---")
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, cpu_heavy, 5_000_000)
        print(f"  CPU 计算结果: {result}")
        print("  (CPU 密集放进程池, I/O 密集放线程池, 协程只负责调度)")

    asyncio.run(run())


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "completed": demo_completed,
        "timeout": demo_timeout,
        "to_thread": demo_to_thread,
        "bug": demo_bug,
        "executor": demo_executor,
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
# asyncio.as_completed() → 谁先完成先处理
# asyncio.timeout(秒)    → 超时保护
# asyncio.to_thread()    → 阻塞 I/O 函数丢线程池 (不卡事件循环)
# run_in_executor()      → 阻塞/CPU 函数丢线程池或进程池
#
# 分工铁律:
#   - 协程里绝不直接调用阻塞函数 (time.sleep / requests 等)
#   - 有 async 版本的库 (aiohttp 等) 用 await
#   - 没有 async 版本的阻塞库 → asyncio.to_thread 包一层
#   - CPU 密集 → run_in_executor 丢进程池
