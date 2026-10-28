"""
描述符协议 (Descriptor Protocol) -- __get__ / __set__ / __delete__

[什么是描述符?]

  描述符就是一个能控制"属性如何被访问"的对象.
  只要一个类实现了以下任一方法, 它的实例就是描述符:

    __get__(self, instance, owner)   → 读取属性时调用
    __set__(self, instance, value)   → 设置属性时调用
    __delete__(self, instance)       → 删除属性时调用

  描述符必须定义为类属性, 不能是实例属性.

[为什么需要描述符?]

  假设你要写一个 Person 类, 要求 age 必须是 int 类型且非负:
    class Person:
        def __init__(self, age):
            self.age = age  # 谁都能设任何值, p.age = "三十岁" 也能通过

  普通 @property 也行, 但如果你有 10 个属性都需要类型检查呢?
  每个都写 @property 会大量重复代码.

  描述符让你把"属性验证逻辑"抽象成一个可复用的类:
    class Person:
        name = LoggedAttribute("name", str)
        age  = LoggedAttribute("age",  int)
        # 所有验证逻辑在 LoggedAttribute 里写一次就够了

  这就是 Django ORM, SQLAlchemy 等框架的底层原理 ──
  你写的 models.CharField(max_length=100) 本质就是一个描述符.

[数据描述符 vs 非数据描述符 -- 这是理解 @property 的关键]

  ┌──────────────┬──────────────────────┬─────────────────────┐
  │ 类型          │ 实现了哪些方法?        │ 查找优先级           │
  ├──────────────┼──────────────────────┼─────────────────────┤
  │ 数据描述符    │ __get__ + __set__     │ 高于实例 __dict__    │
  │              │ 或 __get__ + __delete │ (即 obj.__dict__ 无法 │
  │              │                      │  覆盖数据描述符)      │
  ├──────────────┼──────────────────────┼─────────────────────┤
  │ 非数据描述符  │ 只有 __get__          │ 低于实例 __dict__    │
  │              │                      │ (实例自己的属性优先)   │
  └──────────────┴──────────────────────┴─────────────────────┘

  访问 obj.attr 时的查找顺序:
    1. 数据描述符 (有 __get__ + __set__/__delete__) ← 最高优先级
    2. 实例 __dict__["attr"]
    3. 非数据描述符 (只有 __get__)
    4. 类属性 (普通值)
    5. __getattr__ (如果定义了)

  @property 为什么能工作? 因为它底层就是一个数据描述符!
  property 类实现了 __get__ 和 __set__, 所以优先级高于实例 __dict__.

[描述符的三个参数详解]

  __get__(self, instance, owner):
    - self:      描述符实例本身
    - instance:  调用描述符的那个实例 (类访问时为 None)
    - owner:     实例所属的类

  __set__(self, instance, value):
    - self:      描述符实例本身
    - instance:  调用描述符的那个实例
    - value:     要设置的值

  __delete__(self, instance):
    - self:      描述符实例本身
    - instance:  调用描述符的那个实例

  注: 多个实例共享同一个描述符对象, 所以描述符数据通常存在
  instance.__dict__ 里, 而不是 self 上.

[Python 内置的描述符]

  @property      → 把方法伪装成属性
  @classmethod   → 方法的第一个参数是类 (cls) 而不是实例
  @staticmethod  → 方法不需要 self 或 cls
  __slots__      → 用描述符替代 __dict__, 节省内存

  这些都是用描述符协议实现的, 你可以在 Python 源码里验证.

[运行方式]
  全部: python 07_descriptor.py
  单个: python 07_descriptor.py non_data / data / property / property_vs_direct / property_full / cached / priority
"""

# ============================================================
# 1. 非数据描述符 -- 只实现了 __get__
# ============================================================
def demo_non_data():
    class TenDescriptor:
        """一个描述符, 无论访问什么属性都返回 10"""
        def __get__(self, instance, owner):
            # instance: 调用这个描述符的实例
            # owner:    实例所属的类
            print(f"  __get__(instance={instance}, owner={owner.__name__})")
            return 10

    class MyClass:
        x = TenDescriptor()      # 类属性 x 是一个描述符对象!

    obj = MyClass()
    print("--- 非数据描述符 ---")
    print(f"  obj.x = {obj.x}")  # 不是取实例属性, 而是触发描述符的 __get__
    print(f"  MyClass.x = {MyClass.x}")  # instance 为 None


# ============================================================
# 2. 数据描述符 -- 实现了 __get__ + __set__ (或 __delete__)
# ============================================================
def demo_data():
    # 数据描述符优先级 > 实例属性字典! 这是理解 @property 的关键.

    class LoggedAttribute:
        """一个带类型检查和日志的属性描述符"""
        def __init__(self, name, expected_type, default=None):
            self.name = name            # 属性名
            self.expected_type = expected_type
            self.default = default
            self._storage_name = f"_{name}"   # 实际存储用的名字

        def __get__(self, instance, owner):
            if instance is None:
                return self              # 类访问时返回描述符本身
            # 用 instance.__dict__ 存, 而不用 self, 因为多个实例共享一个描述符
            return instance.__dict__.get(self._storage_name, self.default)

        def __set__(self, instance, value):
            if not isinstance(value, self.expected_type):
                raise TypeError(
                    f"{self.name} 必须是 {self.expected_type.__name__} 类型, "
                    f"实际是 {type(value).__name__}"
                )
            instance.__dict__[self._storage_name] = value
            print(f"  [LOG] {self.name} = {value!r}")

        def __delete__(self, instance):
            del instance.__dict__[self._storage_name]

    class Person:
        name = LoggedAttribute("name", str, "未知")
        age = LoggedAttribute("age", int, 0)

        def __init__(self, name, age):
            self.name = name       # 触发 __set__ !
            self.age = age         # 触发 __set__ !

    print("\n--- 数据描述符 ---")
    p = Person("张三", 30)
    print(f"  p.name = {p.name}")   # 触发 __get__
    print(f"  p.age = {p.age}")

    print("\n  尝试赋值错误类型: ")
    try:
        p.age = "三十岁"            # 触发 __set__ → TypeError!
    except TypeError as e:
        print(f"  捕获: {e}")


# ============================================================
# 3. @property -- 描述符的语法糖 (最常用!)
# ============================================================
def demo_property():
    # @property 本质是 Python 用描述符帮你自动生成的, 不需要手写上面的类.

    class Circle:
        def __init__(self, radius):
            self._radius = radius

        @property                  # 等价于 area = property(area)
        def area(self):
            """面积 = π * r² -- 只读属性"""
            return 3.14159 * self._radius ** 2

        @property
        def radius(self):
            """半径 -- 可读可写"""
            return self._radius

        @radius.setter             # radius = radius.setter(radius_setter)
        def radius(self, value):
            if value < 0:
                raise ValueError("半径不能为负数")
            self._radius = value

        @radius.deleter
        def radius(self):
            print("删除半径, 重置为 0")
            self._radius = 0

    print("\n--- @property ---")
    c = Circle(5)
    print(f"  半径: {c.radius}")
    print(f"  面积: {c.area:.2f}")
    c.radius = 10
    print(f"  修改半径后: {c.radius}, 面积: {c.area:.2f}")
    del c.radius
    print(f"  删除半径后: {c.radius}")

    # area 没有 setter, 所以是只读的
    # c.area = 100  → AttributeError: can't set attribute


# ============================================================
# 4. @property vs 直接访问属性
# ============================================================
def demo_property_vs_direct():
    # 为什么用 @property 而不是直接 self.radius?
    # 因为如果以后需要在取值/赋值时添加逻辑, property 让你不用修改外部代码

    # 反例: 一开始直接暴露属性
    class BadCircle:
        def __init__(self, radius):
            self.radius = radius       # 直接暴露

    # 之后想加验证就麻烦了, 因为外面已经写了 c.radius = xxx
    # 必须改成 @property → 但这是不兼容的改变

    # 正例: 从一开始就用 property 包装
    class GoodCircle:
        def __init__(self, radius):
            self._radius = radius     # 内部用 _radius

        @property
        def radius(self):
            return self._radius

        @radius.setter
        def radius(self, value):
            if value < 0:
                raise ValueError("半径不能为负数")
            self._radius = value
    # 外部始终写 c.radius = xxx, 内部随时可以加逻辑


# ============================================================
# 5. property 的完整写法
# ============================================================
def demo_property_full():
    class Temperature:
        def __init__(self, celsius=0):
            self._celsius = celsius

        def get_celsius(self):
            return self._celsius

        def set_celsius(self, value):
            if value < -273.15:
                raise ValueError("温度不能低于绝对零度 (-273.15°C)")
            self._celsius = value

        def del_celsius(self):
            del self._celsius

        # property(fget, fset, fdel, doc)  -- 和 @property 等价
        celsius = property(get_celsius, set_celsius, del_celsius, "摄氏温度")

    print("\n--- property() 函数写法 ---")
    t = Temperature(25)
    print(f"  {t.celsius}°C")
    t.celsius = 100
    print(f"  {t.celsius}°C")


# ============================================================
# 6. 缓存属性 -- 一个实用的描述符
# ============================================================
def demo_cached():
    class CachedProperty:
        """计算一次后缓存结果的描述符 -- 类似 @functools.cached_property"""
        def __init__(self, func):
            self.func = func
            self.attr_name = func.__name__

        def __get__(self, instance, owner):
            if instance is None:
                return self
            value = self.func(instance)
            # 算完后直接存到实例的 __dict__, 下次访问时实例属性优先于描述符!
            instance.__dict__[self.attr_name] = value
            return value

    class DataLoader:
        def __init__(self):
            self._data = list(range(100))

        @CachedProperty
        def stats(self):
            """第一次访问时计算, 之后直接从 __dict__ 取 (描述符不再触发)"""
            print("  >>> 正在计算 stats...")
            return {
                "sum": sum(self._data),
                "min": min(self._data),
                "max": max(self._data),
            }

    print("\n--- 缓存属性 ---")
    dl = DataLoader()
    print(f"  第一次: {dl.stats}")     # 计算
    print(f"  第二次: {dl.stats}")     # 直接取缓存, 不再计算


# ============================================================
# 7. 描述符优先级
# ============================================================
def demo_priority():
    # 访问 obj.attr 时的查找顺序:
    #   1. 数据描述符 (有 __get__ + __set__ / __delete__)  ← 最高
    #   2. 实例 __dict__
    #   3. 非数据描述符 (只有 __get__)
    #   4. 类属性 (普通值)
    #   5. __getattr__ (如果定义了的话)  ← 最低
    print("\n--- 描述符优先级演示 ---")

    class DataDesc:
        def __get__(self, obj, owner): return "数据描述符的值"
        def __set__(self, obj, val):   print(f"  设置 {val}")

    class NonDataDesc:
        def __get__(self, obj, owner): return "非数据描述符的值"

    class Demo:
        data_attr = DataDesc()       # 数据描述符
        nondata_attr = NonDataDesc() # 非数据描述符

    d = Demo()
    print(f"  数据描述符: {d.data_attr}")

    # 实例 dict 无法覆盖数据描述符
    d.__dict__["data_attr"] = "实例自己的值"
    print(f"  实例 dict 覆盖后: {d.data_attr}")   # 还是描述符的值!

    # 实例 dict 可以覆盖非数据描述符
    d.__dict__["nondata_attr"] = "覆盖了非数据描述符"
    print(f"  覆盖非数据描述符: {d.nondata_attr}") # 实例的值


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "non_data": demo_non_data,
        "data": demo_data,
        "property": demo_property,
        "property_vs_direct": demo_property_vs_direct,
        "property_full": demo_property_full,
        "cached": demo_cached,
        "priority": demo_priority,
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
# 描述符协议:
#   __get__(self, instance, owner)  → 读取时调用
#   __set__(self, instance, value)  → 赋值时调用
#   __delete__(self, instance)      → 删除时调用
#
# 数据描述符 (__get__ + __set__/__delete__) > 实例 __dict__ > 非数据描述符 (只有 __get__)
#
# @property 是描述符的语法糖, 日常开发首选
# 手写描述符用于更复杂的场景: 类型检查, ORM 字段定义, 缓存等
