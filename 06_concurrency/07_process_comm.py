"""
进程间通信 -- Queue / Pipe / Manager

[运行方式]
  全部: python 07_process_comm.py
  单个: python 07_process_comm.py queue / pipe / manager
"""

from multiprocessing import Process, Queue, Pipe, Manager


# ============================================================
# 模块顶层函数 (进程 target 必须能 pickle)
# ============================================================
def producer(q, n):
    for i in range(n):
        q.put(i)
        print(f"  [生产] 放入 {i}")

def consumer(q, n):
    for _ in range(n):
        item = q.get()
        print(f"  [消费] 取出 {item}")

def pipe_sender(conn):
    conn.send("你好, 这是通过管道发来的消息")
    conn.send([1, 2, 3])
    conn.close()

def add_to_dict(shared_dict, key, value):
    shared_dict[key] = value


# ============================================================
# 案例 1: Queue -- 进程安全队列 (最常用)
# ============================================================
def demo_queue():
    print("--- Queue: 进程间生产者消费者 ---")
    q = Queue()
    p1 = Process(target=producer, args=(q, 5))
    p2 = Process(target=consumer, args=(q, 5))
    p1.start()
    p2.start()
    p1.join()
    p2.join()


# ============================================================
# 案例 2: Pipe -- 双向管道 (一对一)
# ============================================================
def demo_pipe():
    print("--- Pipe: 双向管道 ---")
    parent_conn, child_conn = Pipe()
    p = Process(target=pipe_sender, args=(child_conn,))
    p.start()
    print(f"  收到: {parent_conn.recv()}")
    print(f"  收到: {parent_conn.recv()}")
    p.join()


# ============================================================
# 案例 3: Manager -- 共享 dict / list
# ============================================================
def demo_manager():
    print("--- Manager: 多进程共享一个字典 ---")
    with Manager() as manager:
        shared = manager.dict()

        procs = [
            Process(target=add_to_dict, args=(shared, "a", 1)),
            Process(target=add_to_dict, args=(shared, "b", 2)),
            Process(target=add_to_dict, args=(shared, "c", 3)),
        ]
        for p in procs:
            p.start()
        for p in procs:
            p.join()

        print(f"  主进程读到的字典: {dict(shared)}  ← 三个子进程的写入都看到了")


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "queue": demo_queue,
        "pipe": demo_pipe,
        "manager": demo_manager,
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
# 进程内存隔离 → 通信必须显式
# Queue   = 进程安全队列, 传任务/结果首选
# Pipe    = 一对一双向管道, 比 Queue 快
# Manager = 共享 dict/list, 方便但有开销
# Value/Array = 底层共享内存, 需要时再查文档
#
# 使用准则:
#   - 生产者消费者 → Queue
#   - 两个进程点对点 → Pipe
#   - 多个进程共享一份可变状态 → Manager (能不用尽量不用, 性能差)
#   - 通信数据结构尽量简单 (能传基本类型就别传大对象, 要序列化)
