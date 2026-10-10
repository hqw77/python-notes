"""
选型决策树 —— 线程 vs 进程 vs 协程 (面试答案)

【问题场景: 面试官问"什么时候用线程, 什么时候用进程?"】

  这是 Python 并发面试的高频题。回答的关键不是背定义,
  而是能说清"在什么场景下, 选哪个方案, 为什么"。

  核心判断标准只有一个: 任务到底是 I/O 密集还是 CPU 密集。

【完整决策树】

                    你的任务
                       │
           ┌───────────┴───────────┐
           │ 判断: 主要时间花在哪?  │
           └───────────┬───────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
    I/O 密集                      CPU 密集
   (等网络/磁盘/数据库)          (算数/图像/加密)
        │                             │
        ├─ 并发量小(<几十) ─→ 线程池    └──→ 进程池
        │   ThreadPoolExecutor           ProcessPoolExecutor
        │
        ├─ 并发量极大(上万连接) ─→ 协程
        │   asyncio
        │
        └─ 已有 async 框架 ─→ 协程
            (FastAPI 里直接 async def)

【三者对比表 (面试直接背)】

  ┌──────────┬────────────┬────────────┬──────────────┐
  │          │ 线程        │ 进程        │ 协程          │
  ├──────────┼────────────┼────────────┼──────────────┤
  │ 执行方式  │ 并发 (GIL) │ 并行        │ 并发 (单线程) │
  │ 切换开销  │ 中          │ 大          │ 极小          │
  │ 内存共享  │ 是 (要加锁) │ 否 (要通信) │ 是 (单线程)   │
  │ 适合      │ I/O 密集    │ CPU 密集    │ 海量 I/O      │
  │ 并发上限  │ 几十~几百   │ 核心数      │ 上万          │
  │ 代表库    │ threading   │ multiprocessing │ asyncio  │
  └──────────┴────────────┴────────────┴──────────────┘

【一句话总结 (记这句就够面试了)】

  "Python 的 GIL 导致多线程无法加速 CPU 计算, 所以:
   - I/O 密集用线程池 (或协程处理海量连接)
   - CPU 密集用进程池
   - 协程最轻量, 适合高并发 I/O, 但必须配合 async 生态"

【运行方式】
  全部: python 10_how_to_choose.py
  单个: python 10_how_to_choose.py io / cpu / interview
"""

import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


# ============================================================
# 底层任务: 模拟 I/O 密集 和 CPU 密集
# ============================================================
def io_task(name):
    time.sleep(0.5)
    return f"{name} 完成"

def cpu_task(n):
    total = 0
    for i in range(n):
        total += i
    return total


# ============================================================
# 案例 1: I/O 密集 —— 线程池 vs 进程池
# ============================================================
def demo_io():
    print("=== I/O 密集任务: 线程池 vs 进程池 ===\n")
    tasks = [f"任务{i}" for i in range(8)]

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(io_task, tasks))
    t_thread = time.perf_counter() - start

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as pool:
        list(pool.map(io_task, tasks))
    t_process = time.perf_counter() - start

    print(f"  线程池: {t_thread:.2f}s")
    print(f"  进程池: {t_process:.2f}s")
    print(f"  结论: I/O 密集两者差不多, 但线程池更轻量 → 选线程池")


# ============================================================
# 案例 2: CPU 密集 —— 线程池 vs 进程池
# ============================================================
def demo_cpu():
    print("=== CPU 密集任务: 线程池 vs 进程池 ===\n")
    workload = [4_000_000] * 4

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(cpu_task, workload))
    t_thread = time.perf_counter() - start

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as pool:
        list(pool.map(cpu_task, workload))
    t_process = time.perf_counter() - start

    print(f"  线程池: {t_thread:.2f}s  (GIL 限制, 实际串行)")
    print(f"  进程池: {t_process:.2f}s  (真并行)")
    print(f"  结论: CPU 密集进程池完胜 → 选进程池")


# ============================================================
# 案例 3: 面试问答速查
# ============================================================
def demo_interview():
    print("=== 常见面试题与回答要点 ===\n")
    qa = [
        ("Q1: 说说 Python 的 GIL?",
         "全局解释器锁, CPython 里同一时刻只允许一个线程执行字节码。\n"
         "     导致多线程无法利用多核加速 CPU 密集任务; 但 I/O 时会释放 GIL,\n"
         "     所以多线程对 I/O 密集有效。想真正并行得用多进程。"),
        ("Q2: 线程和进程的区别?",
         "线程共享内存、轻量、受 GIL 限制; 进程独立内存、重量、\n"
         "     各自有 GIL 所以能并行。线程切换开销小, 进程创建销毁开销大。"),
        ("Q3: 协程和线程的区别?",
         "协程是单线程内的用户态切换, 无内核切换开销, 极轻量;\n"
         "     线程由操作系统调度, 有切换开销。协程需要事件循环驱动,\n"
         "     配合 async/await, 适合海量 I/O 并发。"),
        ("Q4: 什么时候用多进程?",
         "CPU 密集任务 (计算、图像处理、加密), 因为线程受 GIL 限制\n"
         "     无法并行, 进程能绕过 GIL 真并行。"),
        ("Q5: 什么时候用协程而不是线程?",
         "需要同时处理成千上万个 I/O 连接时 (如 Web 服务器),\n"
         "     协程切换开销极小, 一个线程能调度海量任务, 线程开不了这么多。"),
    ]
    for q, a in qa:
        print(f"  {q}\n    A: {a}\n")


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "io": demo_io,
        "cpu": demo_cpu,
        "interview": demo_interview,
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
# 选型三句话:
#   1. I/O 密集 + 并发量一般 → 线程池 ThreadPoolExecutor
#   2. I/O 密集 + 海量连接    → 协程 asyncio
#   3. CPU 密集               → 进程池 ProcessPoolExecutor
#
# 判断依据: 先分清 I/O 密集还是 CPU 密集, 再选方案。
