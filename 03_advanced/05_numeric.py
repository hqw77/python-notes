"""
数值运算符协议 —— 让对象支持 + - * / 等数学运算

【三种运算符，三个层次】

  ┌──────────────┬─────────────────────────────┬───────────────────────┐
  │ 类别          │ 魔术方法                     │ 语法                  │
  ├──────────────┼─────────────────────────────┼───────────────────────┤
  │              │ __add__  : +   __radd__  :右+│                       │
  │              │ __sub__  : -   __rsub__  :右-│                       │
  │ 算术运算符    │ __mul__  : *   __rmul__  :右*│ a + b, a - b, a * b   │
  │ (返回新对象)  │ __truediv__: / __rtruediv__ │ a / b, a // b, a % b  │
  │              │ __floordiv__: //             │ a ** b                │
  │              │ __mod__  : %                 │                       │
  │              │ __pow__  : ** __rpow__       │                       │
  ├──────────────┼─────────────────────────────┼───────────────────────┤
  │ 增强赋值      │ __iadd__ : +=  __isub__ : - │  a += b, a -= b       │
  │ (修改自身)    │ __imul__ : *=  __itruediv__ │  a *= b, a /= b       │
  ├──────────────┼─────────────────────────────┼───────────────────────┤
  │ 一元运算符    │ __neg__ : -x  __pos__ : +x  │  -a, +a, abs(a)       │
  │              │ __abs__ : abs(x)             │                       │
  └──────────────┴─────────────────────────────┴───────────────────────┘

【调用链路 —— 3 * v 是怎么工作的？】

  当你写 3 * v 时（int 在左，Vector 在右）：
    1. Python 调用 int.__mul__(3, v)
    2. int 不认识 Vector，返回 NotImplemented
    3. Python 不放弃，尝试 Vector.__rmul__(v, 3)
    4. __rmul__ 返回结果 → 成功！

  所以：__mul__ 处理 v * 3，__rmul__ 处理 3 * v。
  如果两边类型都不认识对方，Python 才抛 TypeError。

  r 前缀的含义：r = "reflected"（反射），即操作数位置互换后的版本。

【__add__ vs __iadd__ 的区别】

  __add__  (a + b)  : 返回新对象，不修改 a 和 b
  __iadd__ (a += b) : 修改 a 自身，返回 a（必须返回 self）

  如果你没写 __iadd__ 但写了 __add__：
    a += b  →  Python 降级为 a = a + b  → 调用 __add__，然后重新赋值

  什么时候必须用 __iadd__？
    - 可变对象（list, dict）：+= 应该原地修改，否则和内置行为不一致
    - 不可变对象（int, str, tuple）：__add__ 就够了，反正不能原地修改

  例：
    lst = [1, 2]          num = 10
    lst += [3]             num += 5
    等价于：               等价于：
    lst.__iadd__([3])      num = num.__add__(5)
    原地修改 ↑             创建新 int ↑（int 是 immutable）

【右运算符（__rXXX__）存在的意义】

  不是所有类型都知道怎么和你的类运算：

    class Vector:
        def __mul__(self, scalar):   # Vector * 3 ✓
            ...

    v * 3  ✓  Vector.__mul__(v, 3) → 能做
    3 * v  ✗  int.__mul__(3, v) → NotImplemented
             → Python 尝试 Vector.__rmul__(v, 3) → 能做

  如果你希望你的类能和内置类型混合运算，__rXXX__ 几乎是必须的。

【类型转换魔术方法（额外知识点）】

  __int__(self)    → int(obj)
  __float__(self)  → float(obj)
  __bool__(self)   → bool(obj)（用于 if obj: 判断真值）
  __complex__(self) → complex(obj)

【运行方式】
  全部: python 05_numeric.py
  单个: python 05_numeric.py add / mul / iadd / unary / money / cheatsheet
"""

# ============================================================
# 1. 基础：实现向量加法
# ============================================================
def demo_add():
    class Vector:
        """二维向量"""
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __add__(self, other):
            """self + other → 返回新的 Vector"""
            if isinstance(other, Vector):
                return Vector(self.x + other.x, self.y + other.y)
            return NotImplemented

        def __sub__(self, other):
            """self - other"""
            if isinstance(other, Vector):
                return Vector(self.x - other.x, self.y - other.y)
            return NotImplemented

        def __eq__(self, other):
            if isinstance(other, Vector):
                return self.x == other.x and self.y == other.y
            return NotImplemented

        def __repr__(self):
            return f"Vector({self.x}, {self.y})"

    v1 = Vector(1, 2)
    v2 = Vector(3, 4)
    print("--- 向量加减 ---")
    print(f"  {v1} + {v2} = {v1 + v2}")
    print(f"  {v1} - {v2} = {v1 - v2}")


# ============================================================
# 2. 标量乘法 —— 支持 Vector * 数字 和 数字 * Vector
# ============================================================
def demo_mul():
    class VectorV2:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __mul__(self, scalar):
            """Vector * scalar"""
            if isinstance(scalar, (int, float)):
                return VectorV2(self.x * scalar, self.y * scalar)
            return NotImplemented

        def __rmul__(self, scalar):
            """scalar * Vector —— 当左边 int 不知道怎么乘 Vector 时调用"""
            # Python 先尝试 int.__mul__(3, v) → 返回 NotImplemented
            # 然后尝试 VectorV2.__rmul__(v, 3) → 成功
            return self.__mul__(scalar)   # 直接复用 __mul__
        # Python 的方法调用机制会自动将点号左边的实例作为第一个参数（即 self）传递给方法。

        def __truediv__(self, scalar):
            """Vector / scalar"""
            if isinstance(scalar, (int, float)):
                return VectorV2(self.x / scalar, self.y / scalar)
            return NotImplemented

        def __eq__(self, other):
            if isinstance(other, VectorV2):
                return self.x == other.x and self.y == other.y
            return NotImplemented

        def __repr__(self):
            return f"VectorV2({self.x}, {self.y})"

    v = VectorV2(2, 3)
    print(f"\n--- 标量乘除 ---")
    print(f"  {v} * 3 = {v * 3}")
    print(f"  3 * {v} = {3 * v}")           # __rmul__ 生效
    print(f"  {v} / 2 = {v / 2}")


# ============================================================
# 3. 增强赋值 += -= *=
# ============================================================
def demo_iadd():
    class Counter:
        def __init__(self, value=0):
            self.value = value

        def __iadd__(self, other):
            """self += other → 修改自身并返回自身"""
            self.value += other
            return self          # 必须返回 self

        def __isub__(self, other):
            """self -= other"""
            self.value -= other
            return self

        def __repr__(self):
            return f"Counter({self.value})"

    c = Counter(10)
    print(f"\n--- 增强赋值 ---")
    c += 5
    print(f"  c += 5 → {c}")     # Counter(15)
    c -= 3
    print(f"  c -= 3 → {c}")     # Counter(12)

    # 关键区别：
    #   __add__  返回新对象，原对象不变: c = c + 1
    #   __iadd__ 修改自身，不创建新对象: c += 1
    # 如果没定义 __iadd__，Python 会用 __add__ 代替：c = c.__add__(1)


# ============================================================
# 4. 一元运算符：-x, +x, abs(x)
# ============================================================
def demo_unary():
    class VectorV3:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __neg__(self):
            """-self → 取反"""
            return VectorV3(-self.x, -self.y)

        def __abs__(self):
            """abs(self) → 向量的模（长度）"""
            return (self.x ** 2 + self.y ** 2) ** 0.5

        def __repr__(self):
            return f"VectorV3({self.x}, {self.y})"

    v = VectorV3(3, 4)
    print(f"\n--- 一元运算符 ---")
    print(f"  -{v} = {-v}")
    print(f"  abs({v}) = {abs(v)}")    # 5.0，勾股定理


# ============================================================
# 5. 实用案例：金额类 —— 避免浮点精度问题
# ============================================================
def demo_money():
    class Money:
        """用整数（分）存储金额，避免浮点误差"""
        def __init__(self, amount):
            self.cents = round(amount * 100)      # 转为分存储

        def __add__(self, other):
            if isinstance(other, Money):
                return Money.from_cents(self.cents + other.cents)
            return NotImplemented

        def __sub__(self, other):
            if isinstance(other, Money):
                return Money.from_cents(self.cents - other.cents)
            return NotImplemented

        def __mul__(self, factor):
            if isinstance(factor, (int, float)):
                return Money.from_cents(round(self.cents * factor))
            return NotImplemented

        def __neg__(self):
            return Money.from_cents(-self.cents)

        def __eq__(self, other):
            if isinstance(other, Money):
                return self.cents == other.cents
            return NotImplemented

        def __lt__(self, other):
            if isinstance(other, Money):
                return self.cents < other.cents
            return NotImplemented

        def __repr__(self):
            return f"Money({self.cents / 100:.2f})"

        @classmethod
        def from_cents(cls, cents):
            obj = cls.__new__(cls)
            obj.cents = cents
            return obj

    print(f"\n--- 金额运算 ---")
    a = Money(10.50)
    b = Money(3.25)
    print(f"  {a} + {b} = {a + b}")       # Money(13.75)
    print(f"  {a} - {b} = {a - b}")       # Money(7.25)
    print(f"  {a} * 3 = {a * 3}")         # Money(31.50)
    print(f"  -{a} = {-a}")               # Money(-10.50)
    print(f"  {a} > {b}: {a > b}")        # True（用了 __lt__）


# ============================================================
# 6. 完整运算符速查表
# ============================================================
def demo_cheatsheet():
    """
    算术运算:
      __add__(self, other)  : +            __radd__  : 右 +
      __sub__(self, other)  : -            __rsub__  : 右 -
      __mul__(self, other)  : *            __rmul__  : 右 *
      __truediv__(self, other): /          __rtruediv__: 右 /
      __floordiv__(self, other): // 整除   __rfloordiv__: 右 //
      __mod__(self, other)  : %            __rmod__  : 右 %
      __pow__(self, other)  : **           __rpow__  : 右 **

    增强赋值:
      __iadd__  : +=    __isub__  : -=      __imul__  : *=
      __itruediv__: /=  __ifloordiv__: //=  __imod__  : %=

    一元运算符:
      __neg__  : -x       __pos__  : +x
      __abs__  : abs(x)   __invert__: ~x

    类型转换:
      __int__  : int(x)   __float__ : float(x)
      __bool__ : bool(x)  __complex__: complex(x)
    """


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "add": demo_add,
        "mul": demo_mul,
        "iadd": demo_iadd,
        "unary": demo_unary,
        "money": demo_money,
        "cheatsheet": demo_cheatsheet,
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
# - __add__/__sub__/__mul__/__truediv__ 让对象支持运算
# - __radd__/__rmul__ 等让对象能放在操作数右边（3 * obj）
# - __iadd__/__isub__ 让 += 修改自身（不分配新对象）
# - __neg__/__abs__ 让 -obj 和 abs(obj) 工作
# - 增强赋值必须返回 self
# - NotImplemented 让 Python 尝试右运算符方法
