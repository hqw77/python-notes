"""
线程池 —— concurrent.futures.ThreadPoolExecutor

【问题场景: 手动创建线程有什么问题?】

  前面章节每次都 `Thread(...).start()`, 看着简单, 但真实项目里:
    - 每个请求都开一个新线程 → 线程创建/销毁有开销
    - 1000 个任务 = 1000 个线程 → 内存爆炸、切换频繁
    - 得手动管理 join、收集结果 → 代码啰嗦

  线程池 = 预先创建固定数量的线程, 任务来了排队丢进去。
  → 线程复用, 数量可控, 结果自动收集。

【核心概念】

  ┌─────────────────────────┬─────────────────────────────────────┐
  │ 概念                     │ 解释                                 │
  ├─────────────────────────┼─────────────────────────────────────┤
  │ ThreadPoolExecutor      │ 线程池对象                           │
  │ max_workers             │ 池子里最多几个线程                   │
  │ executor.submit(fn,..) │ 提交任务, 返回 Future                │
  │ Future.result()         │ 取任务结果 (阻塞直到完成)            │
  │ executor.map(fn, iter)  │ 批量提交, 返回结果的迭代器 (保序)    │
  │ as_completed(futures)   │ 谁先完成先返回谁 (不保序)            │
  │ with ThreadPoolExecutor │ 退出时自动 shutdown, 等所有任务完成  │
  └─────────────────────────┴─────────────────────────────────────┘

  submit vs map:
    submit: 逐个提交, 灵活 (可以传不同参数, 逐个取结果)
    map:    批量提交一个可迭代对象, 结果按输入顺序排列

  重要认知:
    线程池是"日常并发任务的第一选择"。绝大多数场景不需要手动 Thread。
    但它仍然受 GIL 限制 → 只适合 I/O 密集 (见 01 章)。

【运行方式】
  全部: python 05_thread_pool.py
  单个: python 05_thread_pool.py submit / map / completed / download / error
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed


# ============================================================
# 案例 1: 基础用法 —— submit + result
# ============================================================
def demo_submit():
    def fetch(url):
        delay = {"a": 1, "b": 2, "c": 3, "d": 1}[url]
        time.sleep(delay)
        return f"{url} 的响应 (耗时 {delay}s)"

    print("--- submit: 提交任务, result 取结果 ---")
    with ThreadPoolExecutor(max_workers=3) as pool:
        future1 = pool.submit(fetch, "a")
        future2 = pool.submit(fetch, "b")
        print(f"  {future1.result()}")
        print(f"  {future2.result()}")


# ============================================================
# 案例 2: map —— 批量提交, 结果保序
# ============================================================
def demo_map():
    def fetch(url):
        delay = {"a": 1, "b": 2, "c": 3, "d": 1}[url]
        time.sleep(delay)
        return f"{url} 的响应 (耗时 {delay}s)"

    print("--- map: 批量提交, 按输入顺序返回 ---")
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = pool.map(fetch, ["a", "b", "c", "d"])
        for r in results:
            print(f"  {r}")
    print(f"  总耗时: {time.perf_counter() - start:.2f}s  (并发执行, 不是 1+2+3+1=7s)")


# ============================================================
# 案例 3: as_completed —— 谁先完成先处理谁
# ============================================================
def demo_completed():
    def fetch(url):
        delay = {"a": 1, "b": 2, "c": 3}[url]
        time.sleep(delay)
        return f"{url} 的响应 (耗时 {delay}s)"

    print("--- as_completed: 不保序, 谁先完成先返回 ---")
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(fetch, url): url for url in ["a", "b", "c"]}
        for future in as_completed(futures):
            url = futures[future]
            print(f"  {url} 先完成: {future.result()}")


# ============================================================
# 案例 4: 实战 —— 并发下载 (I/O 密集)
# ============================================================
def demo_download():
    def download(page):
        time.sleep(0.3)
        return f"页面 {page} 的内容"

    print("--- 实战: 并发下载 20 个页面 ---")
    pages = list(range(20))
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=5) as pool:
        results = list(pool.map(download, pages))
    print(f"  下载了 {len(results)} 个页面")
    print(f"  总耗时: {time.perf_counter() - start:.2f}s")
    print(f"  (20 × 0.3s = 6s 串行, 现在 5 线程并发约 {6/5:.1f}s)")


# ============================================================
# 案例 5: 异常处理 —— 任务出错怎么办
# ============================================================
def demo_error():
    def risky(n):
        if n == 2:
            raise ValueError(f"任务 {n} 出错了")
        return n * 10

    print("--- 异常处理 ---")
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(risky, i) for i in range(4)]
        for i, f in enumerate(futures):
            try:
                print(f"  任务 {i}: {f.result()}")
            except ValueError as e:
                print(f"  任务 {i}: 捕获异常 -> {e}")


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "submit": demo_submit,
        "map": demo_map,
        "completed": demo_completed,
        "download": demo_download,
        "error": demo_error,
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
# ThreadPoolExecutor(max_workers=N) → 创建含 N 个线程的池
# submit(fn, *args) → 提交任务, 返回 Future
# future.result()   → 阻塞取结果
# map(fn, iterable) → 批量提交, 结果保序
# as_completed()    → 按完成顺序返回
# with ...          → 自动等待所有任务完成并关闭池
#
# 使用准则:
#   - max_workers 别乱设: I/O 密集可以设大点 (几十), CPU 密集设成核心数
#   - 线程池适合 I/O 密集; CPU 密集请用进程池 (见 08 章)
#   - 能用线程池就别手写 Thread (复用线程, 代码简洁)
