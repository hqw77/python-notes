"""
进程 —— multiprocessing, 绕过 GIL 做真并行

【问题场景: CPU 密集任务怎么加速?】

  01 章已经演示: 多线程受 GIL 限制, 跑 CPU 密集任务不但不快, 反而更慢。
  要真正"并行", 就得开"进程"。

  进程 vs 线程:
    线程 = 同一个进程内的多条执行流, 共享内存 (受 GIL 限制)
    进程 = 独立的内存空间 + 独立的 Python 解释器 + 独立的 GIL
          → 每个进程有自己的 GIL, 所以能真正并行跑 CPU 任务

  代价: 进程比线程"重"
    - 创建/销毁开销大 (要复制一份解释器)
    - 内存不共享, 通信麻烦 (下一章讲)

【核心概念】

  ┌──────────────────────┬──────────────────────────────────────┐
  │ 概念                  │ 解释                                  │
  ├──────────────────────┼──────────────────────────────────────┤
  │ Process(target=fn)   │ 创建进程                              │
  │ .start()             │ 启动进程                              │
  │ .join()              │ 等进程结束                            │
  │ cpu_count()          │ 查 CPU 核心数                        │
  │ if __name__ == ...   │ Windows 上必须! 否则无限递归创建进程  │
  └──────────────────────┴──────────────────────────────────────┘

【两个 Windows 上的关键约束】

  1. 必须 if __name__ == "__main__":
     Windows 用 spawn 方式启动子进程: 子进程会"重新 import 你的脚本"。
     如果创建进程的代码在模块顶层, 子进程 import 时又再创建进程 → 无限递归。

  2. 进程 target 必须是"模块顶层函数":
     spawn 需要把目标函数 pickle 序列化传给子进程, 而嵌套函数/lambda
     无法被 pickle (报错: Can't get local object)。
     → 所以本文件所有进程入口函数都放在模块顶层, 不能塞进 demo 函数里。

【运行方式】
  全部: python 06_multiprocessing.py
  单个: python 06_multiprocessing.py parallel / shared / return
"""

import time
from multiprocessing import Process, Queue, cpu_count


# ============================================================
# 模块顶层函数 (进程 target 必须能 pickle, 所以不能嵌套定义)
# ============================================================
def cpu_bound(n):
    """纯 CPU 计算"""
    total = 0
    for i in range(n):
        total += i
    return total

shared_value = 0   # 演示"进程不共享变量"用的全局变量

def modify_global():
    """子进程里改这个全局变量 (改的是子进程自己的副本)"""
    global shared_value
    shared_value = 999
    print(f"  子进程里改成了: {shared_value}")

def compute_square(n, result_queue):
    """把结果放进队列传回主进程"""
    result_queue.put(n * n)


# ============================================================
# 案例 1: 多进程真的能并行 (对比实验)
# ============================================================
def demo_parallel():
    N = 30_000_000

    print(f"CPU 核心数: {cpu_count()}\n")

    start = time.perf_counter()
    cpu_bound(N)
    cpu_bound(N)
    single = time.perf_counter() - start
    print(f"  单进程跑 2 次:   {single:.3f}s")

    start = time.perf_counter()
    p1 = Process(target=cpu_bound, args=(N,))
    p2 = Process(target=cpu_bound, args=(N,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    multi = time.perf_counter() - start
    print(f"  2 进程并行跑:     {multi:.3f}s   ← 接近单次的时间!")

    print(f"\n  结论: 多进程把 2 次计算的时间从 {single:.3f}s 压到 {multi:.3f}s")
    print(f"  (多线程做不到这一点, 因为 GIL)")


# ============================================================
# 案例 2: 进程不共享变量 (和线程的关键区别)
# ============================================================
def demo_shared():
    global shared_value
    shared_value = 0

    print("--- 进程不共享内存 ---")
    p = Process(target=modify_global)
    p.start()
    p.join()
    print(f"  主进程里还是: {shared_value}  ← 没被改!")
    print("  (每个进程有独立的内存空间, 改的是子进程自己的副本)")


# ============================================================
# 案例 3: 获取子进程返回值 (Queue 传回结果)
# ============================================================
def demo_return():
    print("--- 进程返回值 (用 Queue 传回) ---")
    q = Queue()
    p = Process(target=compute_square, args=(12, q))
    p.start()
    p.join()
    print(f"  12² = {q.get()}")


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "parallel": demo_parallel,
        "shared": demo_shared,
        "return": demo_return,
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
# Process(target=fn) → 创建进程
# 多进程 = 真并行, 因为每个进程独立 GIL
# 进程不共享内存 → 要通信得用 Queue/Pipe (下一章)
#
# 使用准则:
#   - CPU 密集 → 进程 (或进程池, 见 08 章)
#   - I/O 密集  → 用线程池/协程, 别用进程 (进程重, 不划算)
#   - 进程数别超过 CPU 核心数 (开多了只会频繁切换, 反而慢)
#   - Windows 上: 进程创建放 __main__ 里, target 用模块顶层函数
