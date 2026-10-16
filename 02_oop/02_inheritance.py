"""
继承与多态 —— 复用和扩展类的行为

【继承是什么?】

  子类继承父类的所有属性和方法, 可以重写 (override) 或扩展.
    class Animal:          # 父类 (基类)
        def speak(self):
            return "..."

    class Dog(Animal):     # 子类 (派生类), 继承 Animal
        def speak(self):   # 重写父类方法
            return "汪汪!"

【为什么要用继承?】

  1. 代码复用: 共性放父类, 特性放子类
  2. 多态: 同一接口, 不同行为. dog.speak() 和 cat.speak() 各说各的
  3. 建立类型层级: isinstance(dog, Animal) → True

【Python 的鸭子类型】

  Python 的多态不强制要求继承. 只要对象有 speak() 方法, 就能当 "会叫的动物" 用.
  这叫"鸭子类型": 如果它走路像鸭子, 叫声像鸭子, 那它就是鸭子.

  这和 Java 的风格完全不同: Java 必须 implements Speakable 接口才行.
  Python 更灵活, 但也更容易出错 (没有编译期检查).

【super() —— 调用父类方法】

  super() 让你在子类中调用父类的同名方法. 常用于:
    1. __init__: 子类先用父类的初始化, 再加自己的逻辑
    2. 方法扩展: 子类在父类方法的基础上增加功能

【多继承和 MRO】

  Python 支持多继承: class C(A, B):
  但多继承容易出问题 (钻石继承). Python 用 MRO (Method Resolution Order)
  来决定先找哪个父类. 查看方式: C.__mro__ 或 C.mro().

  MRO 使用 C3 线性化算法.
  记住: 多继承要慎重, Mixin 模式是更好的选择.

【运行方式】
  全部: python 02_inheritance.py
  单个: python 02_inheritance.py single / super / poly / mro / mixin / abc
"""


from abc import ABC, abstractmethod


# ============================================================
# 1. 单继承基础
# ============================================================
# Animal/Dog/Cat 在第 1、2、3 节都被用到, 所以放在模块顶层
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "???"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name!r})"

class Dog(Animal):
    def speak(self):
        return "汪汪!"

class Cat(Animal):
    def speak(self):
        return "喵喵!"


def demo_single():
    print("--- 单继承 ---")

    dog = Dog("旺财")
    cat = Cat("咪咪")
    print(f"  {dog}: {dog.speak()}")
    print(f"  {cat}: {cat.speak()}")
    print(f"  isinstance(dog, Animal): {isinstance(dog, Animal)}")
    print(f"  isinstance(dog, Dog): {isinstance(dog, Dog)}")


# ============================================================
# 2. super() 调用父类
# ============================================================
# Bird 在第 2、3 节都被用到, 所以放在模块顶层
class Bird(Animal):
    def __init__(self, name, can_fly=True):
        super().__init__(name)           # 调用父类的 __init__
        self.can_fly = can_fly

    def speak(self):
        return "叽叽!"

    def info(self):
        return f"{self.name}, {'能飞' if self.can_fly else '不会飞'}"


def demo_super():
    print("\n--- super() ---")

    parrot = Bird("鹦鹉")
    penguin = Bird("企鹅", can_fly=False)
    print(f"  {parrot}: {parrot.info()}")
    print(f"  {penguin}: {penguin.info()}")


# ============================================================
# 3. 多态
# ============================================================
def demo_poly():
    print("\n--- 多态 ---")

    def make_speak(animal):
        """这个函数不关心 animal 是什么类型, 只要它有 speak() 方法就行"""
        return f"{animal.name} 说: {animal.speak()}"

    animals = [Dog("大黄"), Cat("小花"), Bird("小蓝")]
    for a in animals:
        print(f"  {make_speak(a)}")
    # 同一个 make_speak() 函数, 对不同的对象产生不同的行为 —— 这就是多态


# ============================================================
# 4. MRO (Method Resolution Order) —— 方法解析顺序
# ============================================================
def demo_mro():
    # MRO 回答一个问题: 当类有多个父类, 且父类有同名方法时, 先找谁?
    #
    # 类比: 你去三个房间找东西, 必须规定先搜哪个房间.
    # MRO 就是这个"搜索路线图".

    print("\n--- MRO ---")

    # === 场景: 钻石继承 (Diamond Inheritance) ===
    #     A (爷爷)
    #    / \
    #   B   C (爸爸们)
    #    \ /
    #     D (孙子, 继承了 B 和 C)
    #
    # D 要找 who() 方法, 路径是 D → B → C → A → object
    # 这个顺序叫 C3 线性化

    class A:
        def who(self):
            return "A (爷爷)"

    class B(A):
        def who(self):
            return "B (爸爸1)"   # 重写了 A 的 who

    class C(A):
        def who(self):
            return "C (爸爸2)"   # 也重写了 A 的 who

    class D(B, C):        # D 同时继承 B 和 C, B 写在前面意味着 B 优先
        pass               # D 自己没有 who()

    d = D()
    # 关键: d.who() 返回什么? 看 MRO!
    print(f"  d.who() = {d.who()!r}")   # 返回 B 的 → B 在 C 前面

    # 查看 MRO 路线图
    print("  MRO 路线图:")
    for i, c in enumerate(D.__mro__):
        print(f"    [{i}] {c.__name__} → 搜索顺序第 {i+1} 站")
    # 输出: [0] D → [1] B → [2] C → [3] A → [4] object

    # MRO 三大规则:
    #   1. 子类优先于父类 (D 在 B 前面)
    #   2. 声明顺序决定优先级 (class D(B, C) 中 B 比 C 优先)
    #   3. 每个类只出现一次 (爷爷 A 只出现在最后, 不会重复)
    #
    # 可以通过 cls.mro() 或 cls.__mro__ 查看任何类的 MRO

    # === 多继承的实际问题 ===
    # 假设你写了一个类继承两个第三方库的类, 它们都有 save() 方法:
    #   class MyModel(LibA_Model, LibB_Mixin):
    #       pass
    # 那么 save() 会先找 LibA_Model 的, 再找 LibB_Mixin 的.
    # 声明时父类的顺序决定了优先级!


# ============================================================
# 5. Mixin 模式 —— "给类加功能的小零件"
# ============================================================
def demo_mixin():
    # Mixin 就是一个小型类, 它只提供一小块功能, 不单独使用.
    # 你要什么功能, 就"混入"什么 Mixin, 像给手机插扩展卡一样.
    #
    # 核心原则:
    #   1. Mixin 不单独实例化 —— 它只是零件, 不是完整产品
    #   2. Mixin 只做一件事 —— 一个 Mixin 只提供一种功能 (单一职责)
    #   3. Mixin 写在父类列表的第一位 —— class MyClass(Mixin, BaseClass):
    #      这样 MRO 里 Mixin 的方法优先于 BaseClass 的同名方法

    print("\n--- Mixin 模式 ---")

    # === 示例: 给不同类混入相同功能 ===

    # Mixin 1: 转 JSON 的能力
    class JsonMixin:
        """混入: 让任何类拥有 to_json() 方法"""
        def to_json(self):
            import json
            return json.dumps(self.__dict__, ensure_ascii=False)

    # Mixin 2: 日志能力
    class LogMixin:
        """混入: 在属性修改时自动打印日志"""
        def __setattr__(self, name, value):
            print(f"  [LOG] {self.__class__.__name__}.{name} = {value!r}")
            super().__setattr__(name, value)  # 交给真正的 __setattr__ 去存

    # 基类: 提供核心数据
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age

    # 混合使用: 同时混入两种功能
    class LoggedPerson(LogMixin, JsonMixin, Person):
        """既有日志, 又能转 JSON 的 Person"""
        def __init__(self, name, age):
            super().__init__(name, age)

    # 另一种组合: 只需要 JSON, 不需要日志
    class SimplePerson(JsonMixin, Person):
        """能转 JSON 但没日志的 Person"""
        def __init__(self, name, age):
            super().__init__(name, age)

    print("  有日志+JSON 的 Person:")
    lp = LoggedPerson("Alice", 30)    # __setattr__ 会触发日志
    print(f"    to_json: {lp.to_json()}")

    print("\n  只有 JSON 的 Person:")
    sp = SimplePerson("Bob", 25)
    print(f"    to_json: {sp.to_json()}")

    # === Mixin vs 多继承的区别 ===
    # 多继承经常被滥用: class Dog(Animal, Pet, Runnable, Serializable, ...)
    # 这样没人知道你到底是什么. Mixin 解决的就是这个问题:
    #   - 真正的"是什么"放在最后: class MyClass(MixinA, MixinB, BaseClass)
    #   - BaseClass 定义"你是什么" (Person, Animal, Vehicle)
    #   - Mixin 定义"你能干什么" (转 JSON, 记日志, 可序列化)

    # === 实战中你早就用过 Mixin ===
    # Django REST Framework 里到处都是:
    #   class MyView(ListModelMixin, CreateModelMixin, GenericView):
    #       pass
    # 这就是通过 Mixin 给 View 加上了"列表"和"创建"功能

    print(f"\n  LoggedPerson 的 MRO:")
    for c in LoggedPerson.__mro__:
        print(f"    {c.__name__}")


# ============================================================
# 6. 抽象基类 (ABC)
# ============================================================
def demo_abc():
    print("\n--- 抽象基类 ---")

    class Shape(ABC):
        @abstractmethod
        def area(self):
            """子类必须实现这个方法"""
            ...

        @abstractmethod
        def perimeter(self):
            ...

    class Circle(Shape):
        def __init__(self, radius):
            self.radius = radius

        def area(self):
            return 3.14159 * self.radius ** 2

        def perimeter(self):
            return 2 * 3.14159 * self.radius

    c = Circle(5)
    print(f"  圆的面积: {c.area():.2f}, 周长: {c.perimeter():.2f}")

    # 如果不实现抽象方法, 不能实例化:
    # s = Shape()  # TypeError!


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "single": demo_single,
        "super": demo_super,
        "poly": demo_poly,
        "mro": demo_mro,
        "mixin": demo_mixin,
        "abc": demo_abc,
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
# - 继承复用父类代码, 子类可以重写方法
# - super() 调用父类被重写的方法
# - 多态: 同一接口, 不同实现 (鸭子类型)
# - MRO 决定多继承时的查找顺序: Class.__mro__
# - Mixin > 多继承 (组合功能, 不制造复杂的继承链)
# - 抽象基类强制子类实现特定方法
