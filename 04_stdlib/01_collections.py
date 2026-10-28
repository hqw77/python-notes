"""
collections 模块 -- 比内置容器更顺手的容器

[问题场景: 手写"没有就初始化"的代码, 又长又容易错]

  统计词频, 普通写法每次都要 get:
      counts = {}
      for w in words:
          counts[w] = counts.get(w, 0) + 1

  按长度分组, 每次都要 setdefault:
      groups = {}
      for w in words:
          groups.setdefault(len(w), []).append(w)

  用 list 当队列, 队头删除是 O(n):
      queue.pop(0)          # 后面的元素要整体前移

  collections 把这三种高频模式直接做成了容器:
  Counter / defaultdict / deque. 知道它们, 代码能短一半.

[核心概念]

  ┌────────────────┬──────────────────────────────────────────────┐
  │ namedtuple     │ 有字段名的元组: 可读, 省内存, 不可变          │
  │ Counter        │ 计数器: 专治"统计频次"                        │
  │ defaultdict    │ 有默认值的 dict: 专治"没有就初始化"           │
  │ deque          │ 双端队列: 头尾增删都是 O(1)                   │
  │ OrderedDict    │ 有顺序语义的 dict (普通 dict 3.7+ 也有序)    │
  │ ChainMap       │ 多层字典叠加: 查不到就往上找 (配置覆盖)      │
  └────────────────┴──────────────────────────────────────────────┘

[运行方式]
  全部: python 01_collections.py
  单个: python 01_collections.py namedtuple / counter / defaultdict / deque / ordered / chainmap / use_cases
"""

import sys
import time
from collections import (
    namedtuple, Counter, defaultdict, deque, OrderedDict, ChainMap,
)


# ============================================================
# 1. namedtuple -- 有字段名的元组
# ============================================================
def demo_namedtuple():
    print("--- 1. namedtuple: 有名字的元组 ---")

    Point = namedtuple("Point", ["x", "y"])
    p = Point(3, 4)
    print(f"  创建: {p}")
    print(f"  按字段取值: p.x={p.x}, p.y={p.y}")
    print(f"  按索引取值: p[0]={p[0]}, p[1]={p[1]}   (本质还是元组)")
    x, y = p
    print(f"  照样能解包: x={x}, y={y}")

    # 不可变, 但 _replace 可以生成新对象
    p2 = p._replace(x=10)
    print(f"  _replace 生成新对象: {p2}   (原对象仍是 {p})")

    # 转字典
    print(f"  _asdict(): {dict(p._asdict())}")

    # 默认值 (3.7+)
    Point3 = namedtuple("Point3", ["x", "y", "z"], defaults=[0])
    print(f"  带默认值: Point3(1, 2) = {Point3(1, 2)}")

    # 比 dict 省内存, 比普通元组好读
    d = {"x": 3, "y": 4}
    print(f"  内存对比: namedtuple {sys.getsizeof(p)}B  vs  dict {sys.getsizeof(d)}B")

    print("  适用: 函数返回多个值, 且希望调用方按名字取 (别返回裸元组或大 dict)")


# ============================================================
# 2. Counter -- 统计频次
# ============================================================
def demo_counter():
    print("--- 2. Counter: 统计频次 ---")

    c = Counter("abracadabra")
    print(f"  Counter('abracadabra') = {dict(c)}")
    print(f"  最常见的 3 个: {c.most_common(3)}")
    print(f"  取不存在的键返回 0: c['z'] = {c['z']}   (不会 KeyError)")

    words = "the cat the dog the bird cat".split()
    print(f"  词频: {Counter(words).most_common()}")

    # 计数器的加减与集合运算
    a = Counter({"x": 2, "y": 1})
    b = Counter({"x": 1, "z": 3})
    print(f"  a={dict(a)}, b={dict(b)}")
    print(f"  a + b = {dict(a + b)}   (相加)")
    print(f"  a - b = {dict(a - b)}   (相减, 负数和 0 会被丢掉)")
    print(f"  a & b = {dict(a & b)}   (取小)")
    print(f"  a | b = {dict(a | b)}   (取大)")

    print(f"  元素总数: {sum(c.values())}   (3.10+ 可直接用 c.total())")

    # 和手写对比
    text = "apple banana apple cherry apple"
    manual = {}
    for w in text.split():
        manual[w] = manual.get(w, 0) + 1
    print(f"  手写: {manual}   <- Counter(text.split()) 一行搞定")


# ============================================================
# 3. defaultdict -- 没有就初始化
# ============================================================
def demo_defaultdict():
    print("--- 3. defaultdict: 没有就初始化 ---")

    words = ["cat", "dog", "bird", "cow", "duck"]
    groups = defaultdict(list)
    for w in words:
        groups[len(w)].append(w)
    print(f"  按长度分组: {dict(groups)}   <- 不用 setdefault")

    counter = defaultdict(int)
    for ch in "hello":
        counter[ch] += 1
    print(f"  计数: {dict(counter)}   <- 不用 get(ch, 0)")

    tags = defaultdict(set)
    for user, tag in [("a", "py"), ("b", "py"), ("b", "go")]:
        tags[user].add(tag)
    print(f"  用户 -> 标签: {dict(tags)}")

    # 嵌套: 二维计数
    nested = defaultdict(lambda: defaultdict(int))
    for row, col in [("A", "x"), ("A", "y"), ("B", "x"), ("A", "x")]:
        nested[row][col] += 1
    flat = {k: dict(v) for k, v in nested.items()}
    print(f"  二维计数: {flat}")

    # 坑: 读取不存在的键会顺手创建它
    d = defaultdict(list)
    _ = d["不存在的键"]
    print(f"  坑: 读一次 d['不存在的键'] 后, keys() = {list(d)}")
    print("  → 只想查询, 不想创建时, 用 d.get(k) 或 k in d")


# ============================================================
# 4. deque -- 双端队列
# ============================================================
def demo_deque():
    print("--- 4. deque: 双端队列 ---")

    dq = deque([1, 2, 3])
    dq.append(4)
    dq.appendleft(0)
    print(f"  两端插入: {list(dq)}")
    print(f"  两端弹出: popleft()={dq.popleft()}, pop()={dq.pop()}   -> {list(dq)}")

    # maxlen: 只保留最近 N 条, 满了自动挤掉最老的
    recent = deque(maxlen=3)
    for i in range(1, 7):
        recent.append(i)
    print(f"  maxlen=3 依次 append 1..6: {list(recent)}   <- 只剩最近 3 条")

    # 旋转
    dq = deque([1, 2, 3, 4, 5])
    dq.rotate(2)
    print(f"  rotate(2):  {list(dq)}")
    dq.rotate(-2)
    print(f"  rotate(-2): {list(dq)}")

    # 队列语义: list.pop(0) 是 O(n), deque.popleft() 是 O(1)
    n, times = 20000, 2000
    lst = list(range(n))
    t0 = time.perf_counter()
    for _ in range(times):
        lst.pop(0)
    t_list = time.perf_counter() - t0

    dq2 = deque(range(n))
    t0 = time.perf_counter()
    for _ in range(times):
        dq2.popleft()
    t_deque = time.perf_counter() - t0

    print(f"  从队头删 {times} 次: list.pop(0)={t_list * 1000:.1f}ms, "
          f"deque.popleft()={t_deque * 1000:.2f}ms")

    print("  适用: 队列/栈, 滑动窗口, 只保留最近 N 条记录")


# ============================================================
# 5. OrderedDict -- 顺序也是语义
# ============================================================
def demo_ordered():
    print("--- 5. OrderedDict vs 普通 dict ---")

    d = {"b": 1, "a": 2}
    print(f"  普通 dict 3.7+ 也保持插入顺序: {list(d)}")

    od = OrderedDict([("b", 1), ("a", 2)])
    od.move_to_end("b")
    print(f"  move_to_end('b'):             {list(od)}")
    od.move_to_end("b", last=False)
    print(f"  move_to_end('b', last=False): {list(od)}")

    # 相等比较: OrderedDict 顺序敏感, 普通 dict 不敏感
    o1 = OrderedDict([("a", 1), ("b", 2)])
    o2 = OrderedDict([("b", 2), ("a", 1)])
    d1 = {"a": 1, "b": 2}
    d2 = {"b": 2, "a": 1}
    print(f"  OrderedDict 顺序不同 == ? {o1 == o2}")
    print(f"  普通 dict  顺序不同 == ? {d1 == d2}")

    print("  适用: 需要 move_to_end (自己实现 LRU), 或顺序本身要参与比较")


# ============================================================
# 6. ChainMap -- 多层配置
# ============================================================
def demo_chainmap():
    print("--- 6. ChainMap: 多层配置覆盖 ---")

    defaults = {"host": "127.0.0.1", "port": 8000, "debug": False}
    env = {"port": 9000}
    cli = {"debug": True}

    config = ChainMap(cli, env, defaults)
    print(f"  合并后: {dict(config)}")

    print(f"  config['port'] = {config['port']}   <- env 覆盖 defaults")
    print(f"  config['host'] = {config['host']}   <- 只有 defaults 有")

    # 写操作只改第一层
    config["host"] = "example.com"
    print(f"  写入后 cli = {dict(cli)}")
    print(f"  env 仍是 {dict(env)}, defaults 仍是 {dict(defaults)}")

    # new_child: 临时加一层覆盖, 不影响原对象
    temp = config.new_child({"port": 7000})
    print(f"  new_child 后 temp['port'] = {temp['port']}, 原 config['port'] = {config['port']}")

    print("  适用: 配置优先级 (命令行 > 环境变量 > 默认值), 作用域链")


# ============================================================
# 7. 实战: 分析一段访问日志
# ============================================================
def demo_use_cases():
    print("--- 7. 实战: 三个容器配合分析访问日志 ---")

    logs = [
        "10.0.0.1 200 GET /index",
        "10.0.0.2 404 GET /missing",
        "10.0.0.1 200 POST /login",
        "10.0.0.3 500 GET /boom",
        "10.0.0.1 200 GET /index",
        "10.0.0.2 200 GET /index",
    ]

    ip_counter = Counter()          # 每个 IP 的访问次数
    status_groups = defaultdict(list)   # 每个状态码对应哪些路径
    recent = deque(maxlen=3)        # 最近 3 条

    for line in logs:
        ip, status, method, path = line.split()
        ip_counter[ip] += 1
        status_groups[status].append(path)
        recent.append(f"{ip} {status} {path}")

    print(f"  访问最多的 2 个 IP: {ip_counter.most_common(2)}")
    print(f"  状态码分布: {dict(Counter(line.split()[1] for line in logs))}")
    print(f"  每个状态码的路径: {dict(status_groups)}")
    print(f"  最近 3 条: {list(recent)}")

    print("  三个容器各司其职: Counter 计数, defaultdict 分组, deque 保留窗口")


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    demos = {
        "namedtuple": demo_namedtuple,
        "counter": demo_counter,
        "defaultdict": demo_defaultdict,
        "deque": demo_deque,
        "ordered": demo_ordered,
        "chainmap": demo_chainmap,
        "use_cases": demo_use_cases,
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
# 选型速记:
#   统计频次          -> Counter (.most_common() 直接出 Top N)
#   分组 / 计数 / 嵌套 -> defaultdict(list / int / set 或 lambda)
#   队列 / 栈 / 滑动窗 -> deque (头尾 O(1), maxlen 自动限长)
#   多个值返回        -> namedtuple (比 dict 省内存, 比裸元组好读)
#   配置分层          -> ChainMap (写只改第一层, new_child 做临时覆盖)
#   顺序参与比较      -> OrderedDict (普通 dict 比较不看顺序)
#
# 三个坑:
#   1. defaultdict 读取不存在的键会创建它, 只查询用 get / in
#   2. Counter 相减会丢掉 0 和负数, 想保留用 subtract()
#   3. deque 支持随机访问但很慢, 需要索引密集访问就用 list
