# Python 并发编程学习路线

> 一条主线贯穿全程：**GIL 决定了 Python 里「线程 / 进程 / 协程」该怎么选**。
> 不懂 GIL 就学并发，等于不看地图开车。

---

## 前置知识（来自其他阶段）

| 概念 | 来自 | 为什么是前提 |
|---|---|---|
| 生成器 `yield` | `03_advanced/09_generator_advanced.py` | 协程的底层原理 |
| `async/await` 入门 | `03_advanced/10_async_basics.py` | 学协程进阶前先会基础 |

---

## 第一梯队：概念 + 线程（必须按顺序）

| 序号 | 特性 | 文件 | 核心内容 | 能干啥 |
|---|---|---|---|---|
| 01 | 并发 vs 并行 + GIL | `01_concept.py` | 并发/并行、GIL、I/O密集 vs CPU密集 | 建立全局认知，后面全靠它 |
| 02 | 线程 | `02_threading.py` | `Thread`、`start`、`join`、`daemon` | 让多个任务「看起来」同时跑 |
| 03 | 锁 | `03_lock.py` | `Lock`、`RLock`、竞态条件、死锁 | 多线程共享数据不打架 |

---

## 第二梯队：线程进阶 + 线程池（日常最常用）

| 序号 | 特性 | 文件 | 核心内容 | 能干啥 |
|---|---|---|---|---|
| 04 | 同步原语 | `04_sync_primitives.py` | `Semaphore`、`Event`、`Condition`、`Queue` | 限流、信号通知、生产者消费者 |
| 05 | 线程池 | `05_thread_pool.py` | `ThreadPoolExecutor`、`submit`、`map` | 日常并发任务首选，别手写线程 |

---

## 第三梯队：进程（CPU 密集的答案）

| 序号 | 特性 | 文件 | 核心内容 | 能干啥 |
|---|---|---|---|---|
| 06 | 进程 | `06_multiprocessing.py` | `Process`、绕过 GIL、`__main__` 守护 | 加速 CPU 密集计算 |
| 07 | 进程间通信 | `07_process_comm.py` | `Queue`、`Pipe`、`Manager` | 进程间不共享内存，要显式通信 |
| 08 | 进程池 | `08_process_pool.py` | `ProcessPoolExecutor` | CPU 密集任务的池化 |

---

## 第四梯队：协程进阶 + 选型（收尾）

| 序号 | 特性 | 文件 | 核心内容 | 能干啥 |
|---|---|---|---|---|
| 09 | 协程进阶 | `09_coroutine_deep.py` | `asyncio.to_thread`、`run_in_executor`、混用 | 协程 + 线程/进程协同 |
| 10 | 选型决策树 | `10_how_to_choose.py` | 线程 vs 进程 vs 协程对比 | 面试高频，收尾总结 |

---

## 学习建议

1. **01 是地基**：GIL 没搞懂，后面线程、进程、协程的区别全是浆糊。
2. **线程三连**（02→03→04）是一体的，学完 03 立刻看竞态条件示例。
3. **线程池（05）是分水岭**：真实项目里 90% 的并发用 `ThreadPoolExecutor` 就够，手写线程反而少。
4. **进程（06→08）**：只有 CPU 密集才需要，别为了「并发」就上进程，开销大。
5. **协程（09）**：前提是已经学完 `03_advanced/10_async_basics.py`。
6. **10 是面试答案**：把决策树背下来，能覆盖大部分并发面试题。
