"""
类与实例 —— 面向对象编程的基石

【什么是类? 什么是实例?】

  类就是"蓝图", 实例就是按蓝图造出来的"实物".
    class Dog:        ← 类 (蓝图): 狗有名字, 会叫
        ...

    my_dog = Dog()    ← 实例 (实物): 一只叫"旺财"的具体狗

  类定义了一类对象共有的属性 (数据) 和方法 (行为).
  每个实例有自己独立的属性值 (你的狗叫旺财, 我的狗叫来福).

【self 是什么?】

  self 代表"当前这个实例". 当你写 dog.bark() 时:
    1. Python 把 dog 作为第一个参数传入 bark
    2. 所以 bark 的签名是 def bark(self):
    3. self 不是关键字, 只是约定俗成的名字 (你也可以叫 this, 但别这么干)

  从 C++/Java 转过来的话: self ≈ this, 但 Python 必须显式写出 self.

【__init__ 不是构造函数!】

  __init__ 是"初始化方法", 不是真正的构造函数.
  真正的构造函数是 __new__, 它负责创建对象.
  但日常开发中 99.9% 的情况你只需要写 __init__.

  __new__ 创建对象 → __init__ 初始化对象

【实例属性 vs 类属性】

  class Dog:
      species = "犬科"     # 类属性: 所有实例共享

      def __init__(self, name):
          self.name = name  # 实例属性: 每个实例独有

  Dog.species 改了就全改了, dog.name 只改这一只狗.

【属性查找顺序 (关键!)】

  当你写 obj.attr 时, Python 按此顺序查找:
    1. 数据描述符 (__get__ + __set__)
    2. obj.__dict__ (实例自己的属性)
    3. type(obj).__dict__ (类属性)
    4. 父类的 __dict__
    5. __getattr__ (兜底)

  这就是为什么类属性可以被所有实例访问, 但实例属性会覆盖同名类属性.

【运行方式】
  全部: python 01_class_basic.py
  单个: python 01_class_basic.py class / attr / private / slots / builtin
"""


# ============================================================
# 1. 类的定义与实例化
# ============================================================
# Dog 类在第 1、2 节都被用到, 所以放在模块顶层 (demo 函数之前)
class Dog:
    """一个简单的狗类"""
    species = "犬科"          # 类属性

    def __init__(self, name, age):
        self.name = name       # 实例属性
        self.age = age         # 实例属性

    def bark(self):
        """实例方法: 第一个参数必须是 self"""
        return f"{self.name} 说: 汪汪!"

    def info(self):
        return f"{self.name}, {self.age}岁, {self.species}"

# 创建实例 (dog1/dog2 在第 1、2 节都被用到, 也放在模块顶层)
dog1 = Dog("旺财", 3)
dog2 = Dog("来福", 1)


def demo_class():
    print("--- 类与实例 ---")
    print(f"  dog1: {dog1.info()}")
    print(f"  dog2: {dog2.info()}")
    print(f"  {dog1.bark()}")


# ============================================================
# 2. 实例属性 vs 类属性
# ============================================================
def demo_attr():
    print("\n--- 实例属性 vs 类属性 ---")

    print(f"  Dog.species = {Dog.species}")       # 类属性
    print(f"  dog1.species = {dog1.species}")     # 通过实例也能访问类属性

    # 修改类属性 → 所有实例都受影响
    Dog.species = "犬科动物"
    print(f"  修改类属性后: dog1={dog1.species}, dog2={dog2.species}")

    # 修改实例的类属性 → 实际是给实例创建了一个同名实例属性!
    dog1.species = "变异犬"
    print(f"  dog1 改后: dog1.species={dog1.species}, Dog.species={Dog.species}")
    print(f"  dog1.__dict__ = {dog1.__dict__}")   # 能看到 species 出现了
    print(f"  dog2.__dict__ = {dog2.__dict__}")   # 没有 species


# ============================================================
# 3. 私有属性 (约定)
# ============================================================
def demo_private():
    print("\n--- 私有属性约定 ---")

    class BankAccount:
        def __init__(self, owner, balance):
            self.owner = owner          # 公开属性
            self._balance = balance     # _ 前缀: "受保护的", 暗示不要直接访问
            self.__secret = "加密的"    # __ 前缀: 名称改写, 更难从外部访问

        def deposit(self, amount):
            self._balance += amount

        def get_balance(self):
            return self._balance

    acc = BankAccount("Alice", 1000)
    print(f"  acc.owner = {acc.owner}")          # 可以访问
    print(f"  acc._balance = {acc._balance}")    # 可以访问, 但 IDE 会警告你

    # __ 触发名称改写 (name mangling): __secret → _BankAccount__secret
    # print(acc.__secret)  # AttributeError!

    # 推导式拆解: 从 dir(acc) 返回的所有属性名中, 筛选出包含 'secret' 的名字
    # dir(acc) → 返回 acc 所有属性和方法的名称列表
    # [a for a in dir(acc) if 'secret' in a] → 列表推导式: 遍历, 筛选, 收集
    print(f"  改写后的名字: {[a for a in dir(acc) if 'secret' in a]}")

    # 注意: Python 没有真正的 "私有", __ 只是名字改了, 仍然可以访问
    print(f"  强行访问: {acc._BankAccount__secret}")


# ============================================================
# 4. __slots__ 节省内存
# ============================================================
# NormalPerson 在第 4、5 节都被用到, 所以放在模块顶层
class NormalPerson:
    def __init__(self, name, age):
        self.name = name
        self.age = age


def demo_slots():
    print("\n--- __slots__ ---")

    class SlottedPerson:
        __slots__ = ["name", "age"]      # 只允许这两个属性
        def __init__(self, name, age):
            self.name = name
            self.age = age

    np = NormalPerson("Alice", 30)
    sp = SlottedPerson("Bob", 25)
    print(f"  NormalPerson 有 __dict__: {hasattr(np, '__dict__')}")     # True
    print(f"  SlottedPerson 有 __dict__: {hasattr(sp, '__dict__')}")   # False —— 省内存!

    # __slots__ 的代价: 不能动态添加属性
    # sp.email = "bob@test.com"  # AttributeError!


# ============================================================
# 5. 内置工具函数 —— 运行时动态操作对象
# ============================================================
def demo_builtin():
    print("\n--- 内置工具 ---")

    p = NormalPerson("Charlie", 25)

    # type(obj) → 返回对象的类 (这个对象是哪个类造出来的?)
    print(f"  type(p) = {type(p)}")       # <class 'NormalPerson'>

    # isinstance(obj, Class) → 检查 obj 是不是 Class 的实例 (支持继承!)
    # isinstance 比 type(obj) == Class 更好, 因为它会检查整条继承链
    print(f"  isinstance(p, NormalPerson) = {isinstance(p, NormalPerson)}")  # True
    print(f"  isinstance(p, object) = {isinstance(p, object)}")     # True —— 一切皆是 object

    # hasattr(obj, '属性名') → 检查对象有没有这个属性
    print(f"  hasattr(p, 'name'): {hasattr(p, 'name')}")     # True
    print(f"  hasattr(p, 'email'): {hasattr(p, 'email')}")   # False

    # getattr(obj, '属性名'[, 默认值]) → 安全地获取属性值
    # 如果属性存在 → 返回属性值; 如果不存在 → 返回默认值 (不写默认值则抛异常)
    print(f"  getattr(p, 'name'): {getattr(p, 'name')}")             # 'Charlie'
    print(f"  getattr(p, 'email', '未设置'): {getattr(p, 'email', '未设置')}")  # '未设置'


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "class": demo_class,
        "attr": demo_attr,
        "private": demo_private,
        "slots": demo_slots,
        "builtin": demo_builtin,
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
# - 类是蓝图, 实例是实物
# - self 代表当前实例, Python 自动传入
# - __init__ 是初始化方法 (不是构造函数)
# - 类属性所有实例共享, 实例属性各自独立
# - attr是公开属性  _attr 是约定"受保护", __attr 触发名称改写 (都不是真私有)
# - __slots__ 可节省内存, 但禁止动态添加属性
# - type() 看类型, isinstance() 检查继承, hasattr/getattr 动态访问属性
