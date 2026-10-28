"""
并发 vs 并行 + GIL —— 一切并发知识的起点

【运行方式】
  全部: python 01_concept.py
  单个: python 01_concept.py cpu     (只跑 GIL/CPU 密集实验)
        python 01_concept.py io      (只跑 I/O 密集实验)
"""

import time
from threading import Thread
from multiprocessing import Process, cpu_count

N = 20_000_000   # 纯 CPU 计算任务的规模 (从 0 累加到 N)


# ============================================================
# 底层辅助函数 (被两个案例共用)
# ============================================================
def cpu_bound(n):
    """纯计算, 不涉及任何 I/O"""
    total = 0
    for i in range(n):
        total += i
    return total

def run_single():
    start = time.perf_counter()
    cpu_bound(N)
    return time.perf_counter() - start

def run_threads(k):
    threads = [Thread(target=cpu_bound, args=(N,)) for _ in range(k)]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return time.perf_counter() - start

def run_processes(k):
    procs = [Process(target=cpu_bound, args=(N,)) for _ in range(k)]
    start = time.perf_counter()
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    return time.perf_counter() - start

def io_bound(seconds):
    """模拟 I/O: time.sleep 会释放 GIL, 线程等待期间别的线程能跑"""
    time.sleep(seconds)


# ============================================================
# 案例 1: GIL 实验 —— CPU 密集任务 (多线程 vs 单线程 vs 多进程)
# ============================================================
def demo_cpu():
    print(f"这台机器的 CPU 核心数: {cpu_count()}")
    print(f"并行上限: 最多 {cpu_count()} 个进程真正同时跑\n")

    print("CPU 密集任务对比 (跑 2 次同样的计算):\n")

    t1 = run_single()
    print(f"  单线程 跑 1 次:        {t1:.3f}s")

    t2 = run_threads(2)
    print(f"  多线程 跑 2 次:        {t2:.3f}s   ← 没比单线程快多少!")
    print(f"     (因为 GIL: 线程轮流抢锁, 反而多了切换开销)")

    t3 = run_processes(2)
    print(f"  多进程 跑 2 次:        {t3:.3f}s   ← 接近并行, 明显更快")
    print(f"     (因为每个进程独立解释器 + 独立 GIL, 真并行)\n")

    print("结论:")
    print("  CPU 密集 → 线程无效(甚至更慢) → 必须用多进程")


# ============================================================
# 案例 2: I/O 密集任务 —— 为什么线程能加速
# ============================================================
def demo_io():
    print("I/O 密集任务对比 (模拟 4 个各等 1 秒的任务):\n")

    start = time.perf_counter()
    for _ in range(4):
        io_bound(1)
    print(f"  单线程串行:    {time.perf_counter() - start:.2f}s  (4 × 1s)")

    threads = [Thread(target=io_bound, args=(1,)) for _ in range(4)]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"  多线程并发:    {time.perf_counter() - start:.2f}s  (等待重叠, 约 1s)")

    print("\n结论: I/O 等待时 GIL 被释放, 所以线程能让多个 I/O 任务同时等待。")


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {"cpu": demo_cpu, "io": demo_io}
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
# 并发 (concurrency) = 交替执行, 单核也行
# 并行 (parallelism) = 同时执行, 需要多核
# GIL = CPython 同一时刻只允许一个线程执行字节码
#
# 选型速记:
#   I/O 密集  → 线程 (等待时释放 GIL) 或 协程 (更轻量)
#   CPU 密集  → 进程 (独立 GIL, 真并行)
