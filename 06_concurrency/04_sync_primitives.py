"""
线程同步原语 -- Semaphore / Event / Condition / Queue

[问题场景: 锁 (Lock) 只能管"互斥", 管不了更复杂的协作]

  Lock 回答的问题是"谁能进临界区", 但现实里还有别的需求:
    - "最多同时只允许 3 个线程访问数据库"          → Semaphore
    - "等某个线程准备好, 别的线程才开始"            → Event
    - "生产者生产了东西, 通知消费者来拿"            → Condition / Queue
    - "多个线程安全地传递数据"                     → Queue

  这些统称"同步原语"(synchronization primitives).

[核心概念]

  ┌──────────────┬──────────────────────────────────────────────┐
  │ 原语          │ 作用                                          │
  ├──────────────┼──────────────────────────────────────────────┤
  │ Semaphore    │ 信号量: 限制"同时"能进入的线程数 (计数器)      │
  │ Event        │ 事件: 一个线程发信号, 其他线程等这个信号        │
  │ Condition    │ 条件变量: 等待某个条件满足再继续                │
  │ Queue        │ 线程安全队列: 生产者消费者模式的标配            │
  └──────────────┴──────────────────────────────────────────────┘

  Semaphore vs Lock:
    Lock    = 计数为 1 的 Semaphore (要么进要么不进)
    Semaphore(3) = 计数为 3, 最多同时放 3 个线程进去

  Event 的经典场景:
    主线程要等子线程"初始化完成"才能继续 → 子线程 set(), 主线程 wait()

[运行方式]
  全部: python 04_sync_primitives.py
  单个: python 04_sync_primitives.py semaphore / event / condition / queue
"""

import threading
import time
import queue


# ============================================================
# 案例 1: Semaphore -- 限流: 最多同时 N 个线程
# ============================================================
def demo_semaphore():
    def visit_db(semaphore, name):
        with semaphore:          # 拿到名额才进去, 最多 3 个同时
            print(f"  [{name}] 进入数据库连接池 (当前活跃 {3 - semaphore._value} 个)")
            time.sleep(0.5)
            print(f"  [{name}] 离开连接池")

    print("--- Semaphore(3): 限制最多 3 个线程同时访问 ---")
    sem = threading.Semaphore(3)
    threads = [threading.Thread(target=visit_db, args=(sem, f"T{i}")) for i in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("  (6 个线程分两批, 每次最多 3 个同时)")


# ============================================================
# 案例 2: Event -- 一个线程发信号, 其他线程等
# ============================================================
def demo_event():
    def init_system(event):
        print("  初始化线程: 加载配置...")
        time.sleep(2)
        print("  初始化线程: 完成了, 发信号!")
        event.set()

    def wait_init(event, name):
        print(f"  [{name}] 等待初始化完成...")
        event.wait()
        print(f"  [{name}] 收到信号, 开始干活!")

    print("--- Event: 大家都等初始化完成才动 ---")
    ready = threading.Event()
    t = threading.Thread(target=init_system, args=(ready,))
    t.start()
    waiters = [threading.Thread(target=wait_init, args=(ready, f"W{i}")) for i in range(3)]
    for w in waiters:
        w.start()
    t.join()
    for w in waiters:
        w.join()


# ============================================================
# 案例 3: Condition -- 条件变量 (生产者消费者的底层)
# ============================================================
def demo_condition():
    buffer = []
    cond = threading.Condition()

    def producer(items):
        for i in range(items):
            with cond:
                while len(buffer) >= 5:      # 满了就等
                    cond.wait()
                buffer.append(i)
                print(f"  生产 {i} (库存 {len(buffer)})")
                cond.notify()
            time.sleep(0.1)

    def consumer(items):
        for _ in range(items):
            with cond:
                while len(buffer) == 0:      # 空了就等
                    cond.wait()
                item = buffer.pop(0)
                print(f"  消费 {item} (库存 {len(buffer)})")
                cond.notify()
            time.sleep(0.15)

    print("--- Condition: 生产者消费者 (缓冲区上限 5) ---")
    p = threading.Thread(target=producer, args=(8,))
    c = threading.Thread(target=consumer, args=(8,))
    p.start()
    c.start()
    p.join()
    c.join()


# ============================================================
# 案例 4: Queue -- 线程安全队列 (生产者的推荐实现)
# ============================================================
def demo_queue():
    q = queue.Queue(maxsize=5)

    def queue_producer():
        for i in range(8):
            q.put(i)             # 满了会自动阻塞等待
            print(f"  [生产] 放入 {i}")
            time.sleep(0.1)

    def queue_consumer():
        for _ in range(8):
            item = q.get()       # 空了会自动阻塞等待
            print(f"  [消费] 取出 {item}")
            q.task_done()
            time.sleep(0.15)

    print("--- Queue: 更简单的生产者消费者 ---")
    p = threading.Thread(target=queue_producer)
    c = threading.Thread(target=queue_consumer)
    p.start()
    c.start()
    p.join()
    c.join()


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "semaphore": demo_semaphore,
        "event": demo_event,
        "condition": demo_condition,
        "queue": demo_queue,
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
# Semaphore = 限流, 最多 N 个同时 (连接池, 限流器)
# Event     = 信号通知, 等某个标志 (初始化完成, 停止信号)
# Condition = 条件等待, 复杂协作的底层
# Queue     = 线程安全队列, 生产者消费者首选 (内部自带锁)
#
# 经验法则:
#   - 传递数据 → 用 Queue (别自己加锁)
#   - 简单"等一个信号" → 用 Event
#   - 限制并发数 → 用 Semaphore
#   - 只有 Queue/Event/Semaphore 都搞不定 → 才考虑 Condition
