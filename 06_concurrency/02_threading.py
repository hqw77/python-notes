"""
线程基础 -- threading 模块

[运行方式]
  全部: python 02_threading.py
  单个: python 02_threading.py create / join / daemon / shared
"""

import threading
import time


# ============================================================
# 案例 1: 创建线程的两种方式
# ============================================================
def demo_create():
    # 方式一: 直接传函数 (最常用)
    def worker(name, delay):
        print(f"  [{name}] 开始, 在线程 {threading.current_thread().name}")
        time.sleep(delay)
        print(f"  [{name}] 结束")

    print("--- 方式一: 传函数 ---")
    t1 = threading.Thread(target=worker, args=("A", 1), name="线程A")
    t2 = threading.Thread(target=worker, args=("B", 1), name="线程B")
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("两个线程都结束了\n")

    # 方式二: 继承 Thread 重写 run (需要维护状态时用)
    class MyThread(threading.Thread):
        def __init__(self, name, delay):
            super().__init__(name=name)
            self.delay = delay

        def run(self):
            print(f"  [{self.name}] 开始 (继承方式)")
            time.sleep(self.delay)
            print(f"  [{self.name}] 结束 (继承方式)")

    print("--- 方式二: 继承 Thread ---")
    mt = MyThread("C", 0.5)
    mt.start()
    mt.join()


# ============================================================
# 案例 2: join() 的作用 -- 等 vs 不等
# ============================================================
def demo_join():
    def slow_task(name):
        time.sleep(1)
        print(f"  [{name}] 跑完了 (1 秒后)")

    print("--- 不 join: 主线程不等, 程序可能提前退出 ---")
    threading.Thread(target=slow_task, args=("无join",)).start()
    print("  主线程: 我没等它, 直接走到这了\n")

    time.sleep(1.2)   # 稍等一会, 让上面的线程打印出来

    print("--- join: 主线程等它跑完 ---")
    t = threading.Thread(target=slow_task, args=("有join",))
    t.start()
    t.join()
    print("  主线程: 等到了, 它确实跑完了")


# ============================================================
# 案例 3: daemon 守护线程
# ============================================================
def demo_daemon():
    def endless():
        while True:
            time.sleep(0.5)
            print("  [守护线程] 心跳...")

    print("--- daemon=True: 主线程退出, 守护线程跟着结束 ---")
    d = threading.Thread(target=endless, daemon=True)
    d.start()
    time.sleep(1.5)
    print("  主线程: 我要结束了, 守护线程会被自动干掉")
    # 对比: 如果 daemon=False, 上面的 while True 会让程序永远不退出


# ============================================================
# 案例 4: 线程之间共享变量 (引出下一章的锁)
# ============================================================
def demo_shared():
    counter = 0

    def add():
        nonlocal counter
        for _ in range(100_000):
            counter += 1   # 注意: 这行不是原子操作, 理论上有竞争!

    print("--- 线程共享变量 (注意, 详见 03 章第 3 节) ---")
    threads = [threading.Thread(target=add) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"  期望: 400000, 实际: {counter}")
    print("  (这里可能'碰巧'正确 -- GIL 每 5ms 才切换, 窗口太小难复现)")
    print("  (真正的竞态要用'检查+扣款'这类有耗时窗口的操作, 见 03 章)")


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "create": demo_create,
        "join": demo_join,
        "daemon": demo_daemon,
        "shared": demo_shared,
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
# Thread(target=fn)  → 创建线程
# .start()           → 真正开新线程 (不是 .run()!)
# .join()            → 主线程等子线程结束
# daemon=True        → 主线程退出时子线程跟着退出
