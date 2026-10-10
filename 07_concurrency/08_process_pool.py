"""
进程池 —— concurrent.futures.ProcessPoolExecutor

【问题场景: 手动开进程太麻烦】

  手动 Process 的问题和手动 Thread 一样:
    - 每个任务开一个进程, 进程创建开销大 (复制解释器)
    - 100 个任务 = 100 个进程 → 比核心数多, 频繁切换反而慢
    - 结果收集麻烦

  进程池 = 预先创建固定数量的进程 (通常 = CPU 核心数), 任务排队执行。
  和线程池 (05 章) 的 API 几乎一模一样, 只是把 ThreadPoolExecutor
  换成 ProcessPoolExecutor。

【核心概念】

  ┌─────────────────────────┬─────────────────────────────────────┐
  │ 概念                     │ 说明                                 │
  ├─────────────────────────┼─────────────────────────────────────┤
  │ ProcessPoolExecutor     │ 进程池, 适合 CPU 密集                │
  │ max_workers             │ 进程数 (默认 = CPU 核心数)           │
  │ map / submit            │ 和线程池用法完全一致                  │
  └─────────────────────────┴─────────────────────────────────────┘

  线程池 vs 进程池 (一句话区分):
    ThreadPoolExecutor → I/O 密集 (等网络/磁盘)
    ProcessPoolExecutor → CPU 密集 (算数/图像/加密)

【重要提醒】

  - 传给进程池的函数必须是"模块顶层函数" (能被 pickle 序列化),
    不能是 lambda、嵌套函数、类方法 (这些序列化会失败)。
  - Windows 上同样要放 if __name__ == "__main__" 里。

【运行方式】
  全部: python 08_process_pool.py
  单个: python 08_process_pool.py prime / submit / compare
"""

import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


# ============================================================
# 顶层函数 (进程池要求: 必须能 pickle, 所以放模块顶层)
# ============================================================
def is_prime(n):
    """判断一个数是不是质数 (纯 CPU 计算)"""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def heavy_cpu(x):
    """模拟 CPU 密集计算"""
    total = 0
    for i in range(x):
        total += i * i
    return total


# ============================================================
# 案例 1: 进程池基础 —— map 做 CPU 密集计算
# ============================================================
def demo_prime():
    numbers = [1_000_003, 1_000_007, 1_000_019, 999_983, 999_979, 999_961]

    print("--- ProcessPoolExecutor: 并行判断质数 ---")
    start = time.perf_counter()
    with ProcessPoolExecutor() as pool:   # 默认进程数 = CPU 核心数
        results = list(pool.map(is_prime, numbers))
    print(f"  结果: {dict(zip(numbers, results))}")
    print(f"  耗时: {time.perf_counter() - start:.3f}s")
    print(f"  (进程池按 CPU 核心数并行, 比串行快)")


# ============================================================
# 案例 2: submit + result (和线程池一样)
# ============================================================
def demo_submit():
    print("--- submit: 提交任务取结果 ---")
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(is_prime, n) for n in [7, 10, 13, 100]]
        for n, f in zip([7, 10, 13, 100], futures):
            print(f"  {n} 是质数吗? {f.result()}")


# ============================================================
# 案例 3: 对比 —— CPU 密集任务, 进程池 vs 线程池
# ============================================================
def demo_compare():
    workload = [5_000_000] * 4   # 4 个相同的重计算

    print("--- CPU 密集: 进程池 vs 线程池 ---")

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(heavy_cpu, workload))
    t_thread = time.perf_counter() - start
    print(f"  线程池耗时: {t_thread:.3f}s  (受 GIL 限制, 实际串行)")

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as pool:
        list(pool.map(heavy_cpu, workload))
    t_process = time.perf_counter() - start
    print(f"  进程池耗时: {t_process:.3f}s  (真并行)")

    print(f"\n  进程池快了约 {t_thread / t_process:.1f} 倍")


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "prime": demo_prime,
        "submit": demo_submit,
        "compare": demo_compare,
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
# ProcessPoolExecutor → 进程池, CPU 密集首选
# 用法和 ThreadPoolExecutor 完全一样: map / submit / as_completed
# max_workers 默认 = CPU 核心数, 别设超过核心数
#
# 铁律:
#   - CPU 密集 → ProcessPoolExecutor
#   - I/O 密集  → ThreadPoolExecutor
#   - 传参函数必须是顶层函数 (能 pickle)
#   - Windows 上代码放 if __name__ == "__main__" 里
