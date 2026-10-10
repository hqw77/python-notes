"""
锁 —— Lock / RLock, 解决线程数据竞争

【问题场景: 两个线程同时操作同一个变量会怎样?】

  一个"读-改-写"操作, 其实被拆成三步:
    counter += 1  →  1. 读 counter 的值
                     2. 值 + 1
                     3. 写回 counter

  如果两个线程交错执行, 可能发生:
    线程 A: 读 balance = 100
    线程 B: 读 balance = 100   ← A 还没写回, B 读到旧值
    线程 A: 写回 90
    线程 B: 写回 90            ← 两次取款只扣了一次钱

  这就是"竞态条件"(race condition): 结果取决于线程执行的先后顺序。

【核心概念】

  ┌──────────────┬──────────────────────────────────────────────┐
  │ 概念          │ 解释                                          │
  ├──────────────┼──────────────────────────────────────────────┤
  │ 竞态条件      │ 结果取决于执行顺序, 不可预测                    │
  │ Lock         │ 互斥锁: 同一时刻只有一个线程能持有              │
  │ acquire()    │ 拿锁 (阻塞直到拿到)                            │
  │ release()    │ 放锁                                          │
  │ with lock:   │ 推荐写法, 自动 acquire/release, 异常也安全      │
  │ RLock        │ 可重入锁: 同一线程可重复 acquire 不卡死         │
  │ 死锁          │ 两个线程互相等对方放锁, 谁都动不了              │
  └──────────────┴──────────────────────────────────────────────┘

【Lock vs RLock —— 关键区别】

  Lock: 谁拿的锁, 只能谁放。同一线程再次 acquire 会卡死 (死锁)。
  RLock: 记录持有者, 同一线程可以多次 acquire (内部计数), 放同样次数才真正释放。

  什么时候需要 RLock?
  场景: 一个带锁的函数, 内部又调用了另一个带锁的函数。
  → 用 Lock 会死锁, 用 RLock 就没事。

【运行方式】
  全部: python 03_lock.py
  单个: python 03_lock.py race / fix / rlock / deadlock
"""

import threading
import time


# ============================================================
# 案例 1: 竞态条件 —— "先检查后扣款" 不加锁 → 超扣
# ============================================================
def demo_race():
    # 真实场景: 银行取款 = 先查余额 → 判断够不够 → 扣款。三步之间有间隔。
    balance = 1000

    def withdraw_without_lock(amount):
        nonlocal balance
        for _ in range(100):
            if balance >= amount:       # 1. 检查余额够不够
                time.sleep(0.0001)      # 2. 模拟"处理延迟"(这里会被切走!)
                balance -= amount       # 3. 扣款

    print("--- 不加锁: 多线程取款, 余额被扣成负数 ---")
    threads = [threading.Thread(target=withdraw_without_lock, args=(10,)) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"  余额: {balance}  ← 应该是 0, 现在是负数!")
    print(f"  (8 个线程同时'检查'发现余额够, 于是都扣款, 超额扣款了)")


# ============================================================
# 案例 2: 用 Lock 修复 —— 把"检查+扣款"变成原子操作
# ============================================================
def demo_fix():
    balance = 1000
    lock = threading.Lock()

    def withdraw_with_lock(amount):
        nonlocal balance
        for _ in range(100):
            with lock:                  # 锁住整个"检查+扣款", 别人进不来
                if balance >= amount:
                    time.sleep(0.0001)
                    balance -= amount

    print("--- 加锁: 结果正确 ---")
    threads = [threading.Thread(target=withdraw_with_lock, args=(10,)) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"  余额: {balance}  ← 正确归 0!")


# ============================================================
# 案例 3: 为什么 counter += 1 常常"看起来没事"?
# ============================================================
def demo_why_race_hard():
    # 你可能试过这个经典例子, 却发现结果"意外地正确":
    #   counter = 0
    #   def add(): counter += 1   # 4 个线程各加 100 万次
    # 结果却等于 400 万, 没丢更新。为什么?

    # 原因: GIL 每 5ms 才切换一次线程, 而 counter += 1 的"读-改-写"
    # 三步加起来只有几十纳秒。切换点几乎不可能正好落在"读"和"写"之间。
    # → 所以朴素的 counter += 1 在现代 CPython 上很难复现竞态。

    # 但案例 1 的取款例子能稳定复现, 因为 sleep(0.0001) 主动让出 GIL,
    # 把"检查"和"扣款"的间隔拉长到足够被切走。
    # → 真实项目里, 竞态往往藏在"检查+操作"这类有真实耗时的地方。

    print("--- 竞态的真面目 ---")
    print("  竞态需要: 读-改-写 之间有足够的'窗口'让别的线程插进来。")
    print("  counter += 1 窗口太小(纳秒) → 难复现")
    print("  取款(检查+扣款)有真实耗时 → 稳定复现")


# ============================================================
# 案例 4: Lock vs RLock
# ============================================================
def demo_rlock():
    def lock_then_lock_again(lock_obj, name):
        with lock_obj:
            print(f"  [{name}] 第一次拿到锁")
            with lock_obj:   # Lock 会在这里卡死; RLock 没事
                print(f"  [{name}] 第二次拿到锁")

    print("--- Lock 重复加锁 → 死锁 (只打印到第一次) ---")
    t = threading.Thread(target=lock_then_lock_again, args=(threading.Lock(), "Lock"), daemon=True)
    t.start()
    t.join(timeout=1)
    print("  (Lock 卡死在第二次拿锁, 上面只有第一次的打印)\n")

    print("--- RLock 重复加锁 → 正常 ---")
    t = threading.Thread(target=lock_then_lock_again, args=(threading.RLock(), "RLock"))
    t.start()
    t.join()


# ============================================================
# 案例 5: 死锁 —— 交叉拿锁
# ============================================================
def demo_deadlock():
    lock_a = threading.Lock()
    lock_b = threading.Lock()

    def thread1():
        with lock_a:
            time.sleep(0.1)
            with lock_b:           # 等 lock_b, 但被 thread2 占着
                print("  thread1 拿到了两把锁")

    def thread2():
        with lock_b:
            time.sleep(0.1)
            with lock_a:           # 等 lock_a, 但被 thread1 占着
                print("  thread2 拿到了两把锁")

    print("--- 交叉拿锁 → 死锁 ---")
    t1 = threading.Thread(target=thread1, daemon=True)
    t2 = threading.Thread(target=thread2, daemon=True)
    t1.start()
    t2.start()
    t1.join(timeout=1)
    t2.join(timeout=1)
    print("  (两个线程互相等对方, 谁都打印不出来 —— 死锁)")
    print("  解法: 所有线程按相同顺序拿锁 (都先 A 后 B)")


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "race": demo_race,
        "fix": demo_fix,
        "why": demo_why_race_hard,
        "rlock": demo_rlock,
        "deadlock": demo_deadlock,
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
# 竞态条件 = 结果取决于线程执行顺序, 因"读-改-写"非原子引起
# Lock     = 互斥锁, 保证"同一时刻只有一个线程"进临界区
# RLock    = 可重入锁, 同一线程可重复加锁 (解决嵌套加锁死锁)
# with lock = 推荐写法, 自动 acquire/release, 异常也安全
#
# 铁律:
#   1. 共享可变状态 + 多线程 → 必须加锁
#   2. 锁的范围越小越好 (只锁必要代码, 别把 sleep 也锁进去)
#   3. 多把锁时, 所有线程按相同顺序拿锁, 避免死锁
#   4. 优先用 Queue 等线程安全容器, 能不加锁就不加锁 (见 04 章)
