"""
字符串表示协议 -- __str__ 和 __repr__

[问题场景]

  你定义了一个类 Point(x, y), 然后 print(p) 输出:
    <__main__.Point object at 0x000002957F092B40>
  这串东西对调试毫无帮助. 你想输出 Point(x=3, y=4), 怎么办?
  答案: 实现 __repr__ 或 __str__.

[两者的分工]

  ┌──────────┬──────────────────┬──────────────────┬─────────────────────┐
  │          │ 目标读者          │ 谁调用?          │ 追求什么?           │
  ├──────────┼──────────────────┼──────────────────┼─────────────────────┤
  │ __repr__ │ 开发者 (你自己)   │ repr(obj)        │ 清晰, 无歧义         │
  │          │                  │ 交互环境敲变量名   │ 最好能 eval 还原对象  │
  ├──────────┼──────────────────┼──────────────────┼─────────────────────┤
  │ __str__  │ 用户 (使用者)     │ str(obj)         │ 好看, 易懂           │
  │          │                  │ print(obj)       │ 人类友好             │
  └──────────┴──────────────────┴──────────────────┴─────────────────────┘

  生活类比: 去医院看病.
  - __repr__ 是病历: 病人能看懂一部分但不是全懂, 医生能完全看懂
    例: PointV2(x=3, y=4)  - 医生 (开发者)能看到坐标
  - __str__ 是预约单: 只有病人关心, 完全能懂的信息
    例: (3, 4)  - 病人 (用户)只关心坐标长啥样

[调用链路 -- print(obj) 时到底发生了什么?]

  print(obj):
    1. str(obj)  ← print 内部会先调 str()
    2. obj.__str__()  ← str() 去调 __str__
    3. 如果没找到 __str__, 降级用 obj.__repr__()
    4. 如果连 __repr__ 都没找到, 用 object.__repr__() → 输出内存地址

  repr(obj):
    1. 直接调 obj.__repr__()
    2. 如果没找到, 用 object.__repr__()

  所以: 至少实现 __repr__. 有了 __repr__, print 也能降级用它,
  不会出现 <object at 0x...> 这种废输出.

[设计原则]

  __repr__ 的两大追求 (来自官方文档):
    1. 尽可能"像代码"--如果可能, repr(obj) 的返回值应该是能用来重新创建对象的代码
       例: PointV1(x=3, y=4)
    2. 如果做不到 1, 至少包含关键信息, 而不是内存地址

  __str__ 就一个追求: 好看就行.

  f-string 中的强制开关:
    f"{obj}"    默认用 __str__
    f"{obj!s}"  强制用 __str__
    f"{obj!r}"  强制用 __repr__ (调试时很常用)

[运行方式]
  全部: python 01_str_repr.py
  单个: python 01_str_repr.py repr_only / str_and_repr / default / dataclass / tips
"""

from dataclasses import dataclass


# ============================================================
# 共享类 (第 4, 5 节共用): dataclass 自动生成
# ============================================================
@dataclass                       # 自动生成 __init__ __repr__ __eq__ 等方法
class Point:
    x: int
    y: int


# ============================================================
# 1. 只有 __repr__ (没有 __str__)
# ============================================================
def demo_repr_only():
    class PointV1:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __repr__(self):
            # repr 的标准格式: ClassName(参数=值, ...)
            return f"PointV1(x={self.x}, y={self.y})"

    p1 = PointV1(3, 4)
    print("--- 只有 __repr__ ---")
    print(f"  print(): {p1}")                # PointV1(x=3, y=4) - 没有 __str__, 降级用 __repr__
    print(f"  repr():  {repr(p1)}")          # PointV1(x=3, y=4)


# ============================================================
# 2. 同时有 __str__ 和 __repr__
# ============================================================
def demo_str_and_repr():
    class PointV2:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __repr__(self):
            return f"PointV2(x={self.x}, y={self.y})"    # 给开发者: 精确

        def __str__(self):
            return f"({self.x}, {self.y})"               # 给用户: 可读

    p2 = PointV2(3, 4)
    print("\n--- 同时有 __str__ 和 __repr__ ---")
    print(f"  print(): {p2}")                # (3, 4) - 调用 __str__
    print(f"  repr():  {repr(p2)}")          # PointV2(x=3, y=4) - 调用 __repr__

    # 在交互环境中直接输入变量名 → 显示 __repr__
    # >>> p2
    # PointV2(x=3, y=4)


# ============================================================
# 3. 什么都没有 -- 默认行为
# ============================================================
def demo_default():
    class PointV3:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    p3 = PointV3(3, 4)
    print("\n--- 什么都没有 (默认) ---")
    print(f"  print(): {p3}")                # <__main__.PointV3 object at 0x...>
    # 默认显示 类名 + 内存地址, 几乎没用


# ============================================================
# 4. dataclass 自动生成 (实际项目最推荐的方式)
# ============================================================
def demo_dataclass():
    p = Point(3, 4)
    print(f"\n--- dataclass 自动生成 ---")
    print(f"  {p}")                 # Point(x=3, y=4)


# ============================================================
# 5. 实用技巧
# ============================================================
def demo_tips():
    p = Point(3, 4)
    # 容器类 (list/dict)会用子元素的 __repr__ 来显示自身
    print(f"\n--- 容器中的显示 ---")
    print(f"  {[Point(1, 2), Point(3, 4)]}")
    # [Point(x=1, y=2), Point(x=3, y=4)] - 用元素的 __repr__

    # 格式化输出时也可以用
    print(f"\n--- f-string 中的 !r 和 !s ---")
    print(f"  !r 强制用 repr: {p!r}")     # Point(x=3, y=4)
    print(f"  !s 强制用 str:  {p!s}")     # Point(x=3, y=4)  (dataclass 两者一样)


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "repr_only": demo_repr_only,
        "str_and_repr": demo_str_and_repr,
        "default": demo_default,
        "dataclass": demo_dataclass,
        "tips": demo_tips,
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
# - __repr__: 给开发者看, repr() 调用, 写日志用这个
# - __str__:  给用户看, str() 和 print() 调用
# - print() 先找 __str__, 没有就用 __repr__
# - 实际项目推荐用 dataclass, 自动生成这些方法
