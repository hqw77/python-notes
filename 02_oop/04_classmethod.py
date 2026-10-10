"""
类方法、静态方法、特殊方法 —— 面向对象的进阶工具

【三种方法对比】

  ┌──────────────┬──────────┬────────────────────┬──────────────┐
  │ 方法类型      │ 装饰器    │ 第一个参数          │ 能访问什么？  │
  ├──────────────┼──────────┼────────────────────┼──────────────┤
  │ 实例方法      │ (无)     │ self → 实例         │ 实例属性, 类  │
  │ 类方法        │@classmethod│ cls → 类           │ 类属性, 类    │
  │ 静态方法      │@staticmethod│ (无自动参数)       │ 参数里的东西   │
  └──────────────┴──────────┴────────────────────┴──────────────┘

【什么时候用哪个?】

  实例方法: 需要访问实例数据 (self.xxx) → 最常见, 90% 的方法
  类方法: 不需要实例, 但需要访问类 (cls) → 工厂方法, 处理类属性
  静态方法: 不需要实例也不需要类 → 纯工具函数, 放在类里只是因为逻辑相关

【__new__ —— 真正的构造函数】

  __new__ 在 __init__ 之前调用, 负责创建对象 (分配内存).
  你几乎不需要重写它, 除非:
    1. 单例模式 (singleton)
    2. 继承不可变类型 (int, str, tuple) —— 因为不可变类型在 __init__ 之前就已经定值了

  __new__ 是静态方法 (不需要 @staticmethod 装饰器, Python 特殊处理).

  attr  (attribute属性)

【运行方式】
  全部: python 04_classmethod.py
  单个: python 04_classmethod.py methods / factory / new / magic
"""


# ============================================================
# 1. 实例方法 vs 类方法 vs 静态方法
# ============================================================
def demo_methods():
    print("--- 三种方法对比 ---")

    class Demo:
        class_attr = "我是类属性"

        def instance_method(self):
            """实例方法: 可以访问实例和类"""
            return f"实例方法: self={self}"

        @classmethod
        def class_method(cls):
            """类方法: 可以访问类, 不能访问实例"""
            return f"类方法: cls={cls.__name__}, class_attr={cls.class_attr!r}"

        @staticmethod
        def static_method(x, y):
            """静态方法: 就是个普通函数, 放在类里只是为了归类"""
            return x + y

    print(f"  从类调用:")
    print(f"    {Demo.class_method()}")
    print(f"    static_method(3, 5) = {Demo.static_method(3, 5)}")

    print(f"  从实例调用:")
    d = Demo()
    print(f"    {d.instance_method()}")
    print(f"    {d.class_method()}")      # 也能从实例调用, cls 自动传入
    print(f"    static_method = {d.static_method(3, 5)}")

    # 三种方式都能工作, 但语义不同:
    #   Demo.class_method()   ← 推荐: 类方法从类调用
    #   d.instance_method()   ← 唯一: 实例方法只能从实例调用 (或显式传 self)
    #   Demo.static_method()  ← 推荐: 静态方法从类调用


# ============================================================
# 2. 类方法的经典用途: 工厂方法
# ============================================================
def demo_factory():
    print("\n--- 工厂方法 ---")

    class Person:
        def __init__(self, name, birth_year):
            self.name = name
            self.birth_year = birth_year

        @classmethod
        def from_birth_string(cls, s):          # 从 "Alice,1990" 创建
            name, year = s.split(",")
            return cls(name, int(year))

        @classmethod
        def from_dict(cls, d):                  # 从字典创建
            return cls(d["name"], d["birth_year"])

        @property
        def age(self):
            import datetime
            return datetime.datetime.now().year - self.birth_year

        def __repr__(self):
            return f"Person({self.name!r}, {self.birth_year})"

    # 三种创建方式, 调的都是同一个 __init__
    p1 = Person("Alice", 1990)
    p2 = Person.from_birth_string("Bob,1985")
    p3 = Person.from_dict({"name": "Charlie", "birth_year": 2000})
    print(f"  p1 = {p1}")
    print(f"  p2 = {p2}")
    print(f"  p3 = {p3}")


# ============================================================
# 3. __new__: 真正的构造函数
# ============================================================
def demo_new():
    print("\n--- __new__ ---")

    # 示例1: 单例模式
    class Singleton:
        _instance = None

        def __new__(cls):
            if cls._instance is None:
                cls._instance = super().__new__(cls)  # object.__new__ 分配内存
            return cls._instance

    s1 = Singleton()
    s2 = Singleton()
    print(f"  单例: s1 is s2 → {s1 is s2}")    # True, 同一个对象

    # 示例2: 继承不可变类型
    class UpperStr(str):
        def __new__(cls, value):
            return super().__new__(cls, value.upper())  # 在创建时就转大写

    us = UpperStr("hello")
    print(f"  UpperStr: {us}")                  # HELLO


# ============================================================
# 4. 其他常用魔术方法速览
# ============================================================
def demo_magic():
    print("\n--- 其他魔术方法 ---")

    class MagicDemo:
        def __init__(self, value):
            self.value = value

        def __repr__(self):
            return f"MagicDemo({self.value!r})"

        def __bool__(self):
            """bool(obj) 和 if obj: 时调用"""
            return self.value > 0

        def __len__(self):
            """len(obj) 时调用"""
            return abs(self.value)

        def __hash__(self):
            """hash(obj) 时调用, 让对象可哈希 (能放进 set 和 dict key)"""
            return hash(self.value)

    md_pos = MagicDemo(10)
    md_neg = MagicDemo(-5)

    print(f"  {md_pos}, bool → {bool(md_pos)}, len → {len(md_pos)}")
    print(f"  {md_neg}, bool → {bool(md_neg)}, len → {len(md_neg)}")

    # __hash__ 和 __eq__: 如果想放进 set, 两者都要实现
    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y

        def __eq__(self, other):
            return self.x == other.x and self.y == other.y

        def __hash__(self):
            return hash((self.x, self.y))    # 用 tuple 的哈希

        def __repr__(self):
            return f"Point({self.x}, {self.y})"

    points = {Point(1, 2), Point(3, 4), Point(1, 2)}
    print(f"\n  集合自动去重: {points}")       # Point(1, 2) 只有一个


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "methods": demo_methods,
        "factory": demo_factory,
        "new": demo_new,
        "magic": demo_magic,
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
# - 实例方法 (self): 需要操作实例数据 → 90% 的方法
# - 类方法 (cls, @classmethod): 工厂方法, 处理类属性
# - 静态方法 (@staticmethod): 纯工具函数, 和类逻辑相关但不需要 self/cls
# - __new__ 创建对象 (少用), __init__ 初始化对象 (常用)
# - __bool__ 控制 if obj: 的行为
# - __hash__ + __eq__ 让对象可哈希 (放进 set/dict key)
# - 更多魔术方法见 03_advanced/
