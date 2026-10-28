# 并发编程 `06_concurrency/`

学习顺序、核心概念、选型决策树见 [concurrency_roadmap.md](concurrency_roadmap.md)。

配套长文教程：[docs/并发编程.md](docs/并发编程.md)（11 章，每章按「为什么 → 概念 → 案例 → 误区 → 总结」展开，含运行结果与面试问答）

| # | 文件 | 内容 | 状态 |
|---|---|---|---|
| 01 | 01_concept.py | 并发 vs 并行、GIL、I/O密集 vs CPU密集 | ✅ 有案例 |
| 02 | 02_threading.py | Thread 创建、daemon、join | ✅ 有案例 |
| 03 | 03_lock.py | Lock / RLock、竞态条件、死锁 | ✅ 有案例 |
| 04 | 04_sync_primitives.py | Semaphore / Event / Condition / Queue | ✅ 有案例 |
| 05 | 05_thread_pool.py | ThreadPoolExecutor、submit/map | ✅ 有案例 |
| 06 | 06_multiprocessing.py | Process、绕过 GIL | ✅ 有案例 |
| 07 | 07_process_comm.py | 进程间通信 Queue/Pipe/Manager | ✅ 有案例 |
| 08 | 08_process_pool.py | ProcessPoolExecutor | ✅ 有案例 |
| 09 | 09_async_basics.py | 协程基础：async/await、gather、create_task | ✅ 有案例 |
| 10 | 10_coroutine_deep.py | 协程进阶、与线程/进程混用 | ✅ 有案例 |
| 11 | 11_how_to_choose.py | 线程 vs 进程 vs 协程 选型决策树 | ✅ 有案例 |

---

## 一分钟速记

```
                    ┌─ I/O 密集（网络/文件/数据库）
        ┌─ 并发量小 ──→ 线程池 ThreadPoolExecutor
        │
任务 ────┤            ┌─ 并发量极大（上万个连接）──→ 协程 asyncio
        └─ I/O 密集 ──┤
                     └─ 需要简单、能接受线程开销 ──→ 线程池

        └─ CPU 密集（计算/图像/加密）──→ 进程池 ProcessPoolExecutor
```

**核心一句话**：GIL 让线程只能「切换」不能「并行」，所以 CPU 密集靠进程，海量 I/O 靠协程，一般 I/O 用线程池。

---

## 运行方式

每个文件里的每个知识点都封装成独立函数，支持**跑全部**或**跑单个案例**：

```bash
# 跑该文件全部案例
python 06_concurrency/03_lock.py

# 只跑其中一个案例（例：死锁）
python 06_concurrency/03_lock.py deadlock

# 不知道有哪些案例，随便传个不存在的名字会列出可选列表
python 06_concurrency/03_lock.py xxx
```

各文件可选的案例名，见每个文件顶部 docstring 里的【运行方式】。
