"""
封装与属性管理 —— 控制数据的访问方式

【Python 的封装哲学】

  "我们都是成年人." —— Python 社区名言

  Python 没有真正的 private/protected 关键字. 一切都是公开的.
  封装靠的是约定和信任, 而不是编译器强制.

  _属性:   单下划线, "请勿直接访问" (约定)
  __属性:  双下划线, 名称改写 (name mangling), 防止子类意外覆盖
  __xxx__: 双下划线包围, Python 自己的魔术方法, 自己不要这么命名

【名称改写 (Name Mangling) 的机制】

  class Foo:
      def __init__(self):
          self.__secret = 42

  Foo.__secret 不存在! 它在编译期被自动改名为 _Foo__secret.
  目的不是"私有", 而是防止子类意外覆盖同名属性.

【什么时候用 @property? 装饰器】

  1. 计算属性 (derived attribute): area 由 radius 计算, 不需要单独存储
  2. 数据验证: 赋值时检查值的合法性
  3. 向后兼容: 本来直接暴露 self.radius, 后来想加验证, 用 @property 不改外部代码

  但不要过度使用: 如果只是简单的 get/set, 没有验证逻辑,
  直接暴露属性名更好 (Pythonic).
"""

# ============================================================
# 1. 封装约定: _ 和 __
# ============================================================
print("--- 封装约定 ---")

class Employee:
    def __init__(self, name, salary):
        self.name = name            # 公开: 随便访问
        self._department = "技术部"  # 受保护: 暗示不要直接访问
        self.__salary = salary      # 私有: 名称改写

    def get_salary(self):
        return self.__salary

    def set_salary(self, value):
        if value > 0:
            self.__salary = value

emp = Employee("Alice", 10000)
print(f"  name (公开): {emp.name}")
print(f"  _department: {emp._department}")     # 能访问, IDE 会提示
print(f"  get_salary(): {emp.get_salary()}")
# print(emp.__salary)                          # AttributeError!
print(f"  实际存储名为: {[a for a in dir(emp) if 'salary' in a]}")

# ============================================================
# 2. @property 基础
# ============================================================
print("\n--- @property ---")

class Circle:
    def __init__(self, radius):
        self._radius = radius       # 内部存储用 _radius

    @property                       # getter: c.radius 看起来像直接读属性
    def radius(self):
        """半径 —— 可读可写"""
        return self._radius

    @radius.setter                  # setter: c.radius = 5 触发这个方法
    def radius(self, value):
        if value < 0:
            raise ValueError("半径不能为负数")
        self._radius = value

    @radius.deleter                 # deleter: del c.radius 触发
    def radius(self):
        print("  重置半径为 0")
        self._radius = 0

    @property                       # 只读属性 (只有 getter, 没有 setter)
    def area(self):
        """面积 = πr^2 — 只读"""
        return 3.14159 * self._radius ** 2

    @property
    def diameter(self):
        """直径 = 2r — 只读"""
        return 2 * self._radius

c = Circle(5)
print(f"  半径: {c.radius}")           # c.radius (看起来是属性, 实际调了 getter)
print(f"  面积: {c.area:.2f}")         # 只读计算属性
print(f"  直径: {c.diameter:.2f}")
c.radius = 10                          # 调 setter, 会做验证
print(f"  修改后: 半径={c.radius}, 面积={c.area:.2f}")

try:
    c.radius = -5
except ValueError as e:
    print(f"  验证生效: {e}")

# c.area = 100  # AttributeError! 只读属性不能赋值

# ============================================================
# 3. property() 函数写法 (等价于 @property 装饰器)
# ============================================================
print("\n--- property() 函数写法 ---")

class Rectangle:
    def __init__(self, width, height):
        self._width = width
        self._height = height

    def get_width(self):
        return self._width

    def set_width(self, value):
        if value <= 0:
            raise ValueError("宽度必须大于 0")
        self._width = value

    # property(fget, fset, fdel, doc)
    width = property(get_width, set_width, None, "矩形的宽度")

r = Rectangle(10, 5)
print(f"  r.width = {r.width}")
r.width = 20
print(f"  r.width = {r.width}")

# ============================================================
# 4. 直接从公开属性改为 @property (向后兼容)
# ============================================================
print("\n--- 向后兼容示例 ---")

# 假设 v1.0: 直接暴露属性
# class Product:
#     def __init__(self, price):
#         self.price = price

# v2.0: 想加验证, 用 @property 包装, 外部代码不需要改!
class Product:
    def __init__(self, price):
        self._price = price

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value < 0:
            raise ValueError("价格不能为负")
        self._price = value

p = Product(99.9)
print(f"  p.price = {p.price}")
p.price = 199.9                        # 外部调用方式不变!
print(f"  p.price = {p.price}")

# ============================================================
# 总结
# ============================================================
# - Python 封装靠约定: _protected, __name_mangled
# - __attr 的实际名字是 _ClassName__attr (防止子类覆盖)
# - @property 把方法伪装成属性, 用于计算属性和数据验证
# - 没有验证逻辑的话, 直接暴露属性就好, 不要写空壳 getter/setter
# - 描述符 (见 03_advanced) 是 @property 的底层实现
