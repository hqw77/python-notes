# 面向对象编程 (OOP) 笔记

## 目录

1. [类与实例](#1-类与实例)
2. [self 是什么](#2-self-是什么)
3. [__init__ vs __new__](#3-__init__-vs-__new__)
4. [实例属性 vs 类属性](#4-实例属性-vs-类属性)
5. [属性查找顺序](#5-属性查找顺序)
6. [继承与多态](#6-继承与多态)
7. [MRO 方法解析顺序](#7-mro-方法解析顺序)
8. [Mixin 模式](#8-mixin-模式)
9. [封装: _ 和 __](#9-封装-_-和-__)
10. [@property 装饰器](#10-property-装饰器)
11. [三种方法对比](#11-三种方法对比)
12. [工厂方法与单例](#12-工厂方法与单例)
13. [内置工具函数](#13-内置工具函数)

---

## 1. 类与实例

- **类**: 蓝图, 模板, 定义了一类对象共有的属性和方法
- **实例**: 按蓝图造出来的具体对象, 每个实例有自己独立的属性值

```python
class Dog:
    species = "犬科"
    def __init__(self, name, age):
        self.name = name
        self.age = age

my_dog = Dog("旺财", 3)    # 实例化
```

## 2. self 是什么

- `self` 代表"当前这个实例"
- 当你写 `dog.bark()` 时, Python 自动把 `dog` 作为第一个参数传入 `bark`
- `self` 不是关键字, 只是约定俗成 (C++/Java 等价物: `this`)

```python
def bark(self):
    return f"{self.name} 说: 汪汪!"

# dog.bark() → 等价于 Dog.bark(dog)
```

## 3. __init__ vs __new__

```
__new__ 创建对象 → __init__ 初始化对象
(真正构造函数)      (初始化方法)
```

- `__new__`: 分配内存, 创建对象. 日常 99.9% 不需要重写
- `__init__`: 初始化对象属性. 日常 99.9% 只需要写这个
- 需要重写 `__new__` 的场景: 单例模式, 继承不可变类型 (int/str/tuple)

## 4. 实例属性 vs 类属性

| | 实例属性 | 类属性 |
|---|---|---|
| 定义位置 | `self.xxx = ...` | 类体内直接赋值 |
| 作用范围 | 每个实例独有 | 所有实例共享 |
| 修改影响 | 只改这一只狗 | 所有实例都受影响 |
| 典型场景 | `name`, `age` | `species`, 配置, 计数器 |

```python
class Dog:
    species = "犬科"         # 类属性: 所有狗共享

    def __init__(self, name):
        self.name = name     # 实例属性: 每条狗独有
```

**陷阱**: `dog1.species = "xxx"` 实际是给 dog1 创建了同名的实例属性, 不会修改类属性

## 5. 属性查找顺序

访问 `obj.attr` 时, Python 按此顺序查找:

```
1. 数据描述符 (__get__ + __set__)  ← 最高优先级
2. obj.__dict__                    ← 实例自己的属性
3. type(obj).__dict__              ← 类属性
4. 父类的 __dict__                 ← 继承链
5. __getattr__                     ← 兜底
```

## 6. 继承与多态

**继承**: 子类继承父类的所有属性和方法, 可以重写 (override) 或扩展.

```python
class Animal:
    def speak(self):
        return "???"

class Dog(Animal):
    def speak(self):           # 重写父类方法
        return "汪汪!"
```

**多态**: 同一接口, 不同实现. 同一个 `make_speak(animal)` 函数, 对 Dog/Cat/Bird 产生不同行为.

**鸭子类型**: Python 的多态不强制要求继承. 只要对象有 `speak()` 方法, 就能当"会叫的动物"用. "如果它走路像鸭子, 叫声像鸭子, 那它就是鸭子." (vs Java 必须 `implements Speakable`)

**super()**: 在子类中调用父类的同名方法, 常用于 `__init__` 或方法扩展.

**抽象基类 (ABC)**:

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        ...              # 子类必须实现

class Circle(Shape):
    def area(self):
        return 3.14159 * self.radius ** 2
# Shape() → TypeError! 抽象类不能实例化
```

## 7. MRO 方法解析顺序

MRO (Method Resolution Order) 是多继承时的"方法搜索路线图".

**钻石继承**:

```
     A (爷爷)
    / \
   B   C (爸爸们)
    \ /
     D (孙子, 继承 B 和 C)
```

D 的方法搜索路线: `D → B → C → A → object`

**三大规则**:
1. 子类优先于父类 (D 在 B 前面)
2. 声明顺序决定优先级 (`class D(B, C)` 中 B 比 C 优先)
3. 每个类只出现一次

查看 MRO: `ClassName.__mro__` 或 `ClassName.mro()`

## 8. Mixin 模式

Mixin 是"给类加功能的小零件", 用组合替代深层多继承.

**核心原则**:
1. Mixin 不单独实例化 —— 只是零件, 不是完整产品
2. Mixin 只做一件事 —— 一个 Mixin 只提供一种功能
3. Mixin 写在父类列表的第一位: `class MyClass(MixinA, MixinB, BaseClass)`

```python
class JsonMixin:
    """给任何类增加 to_json() 方法"""
    def to_json(self):
        import json
        return json.dumps(self.__dict__, ensure_ascii=False)

class Person(JsonMixin):    # Person "混入"了 JSON 序列化能力
    ...
```

- BaseClass 定义"你是什么" (Person, Animal)
- Mixin 定义"你能干什么" (转JSON, 记日志)

## 9. 封装: _ 和 __

Python 的封装哲学: "我们都是成年人." 没有真正的 private, 全靠约定.

| 写法 | 含义 | 本质 |
|---|---|---|
| `attr` | 公开属性 | 随便访问 |
| `_attr` | 受保护 | 约定: "请勿直接访问", IDE 会提示 |
| `__attr` | 名称改写 | 编译期自动变成 `_ClassName__attr` |
| `__attr__` | Python 魔术方法 | 自己不要这样命名 |

**名称改写的目的是防止子类意外覆盖, 不是实现 private!**

## 10. @property 装饰器

把方法伪装成属性, 用于:
1. 计算属性 (area 由 radius 计算)
2. 数据验证 (赋值时检查值)
3. 向后兼容 (先暴露属性, 后加验证, 外部代码不改)

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property              # getter
    def radius(self):
        return self._radius

    @radius.setter         # setter
    def radius(self, value):
        if value < 0:
            raise ValueError("半径不能为负数")
        self._radius = value

    @property              # 只读 (无 setter)
    def area(self):
        return 3.14159 * self._radius ** 2
```

不要过度使用: 如果没有验证逻辑, 直接暴露属性更好.

`property(fget, fset, fdel, doc)` 函数写法和 `@property` 装饰器等价.

## 11. 三种方法对比

| 方法类型 | 装饰器 | 第一个参数 | 能访问 | 用途 |
|---|---|---|---|---|
| 实例方法 | 无 | `self` | 实例属性 + 类 | 需要操作实例数据 (90%) |
| 类方法 | `@classmethod` | `cls` | 类属性 | 工厂方法, 处理类属性 |
| 静态方法 | `@staticmethod` | 无自动参数 | 参数里的 | 纯工具函数, 放类里归类 |

调用建议:
- `Demo.class_method()` — 类方法从类调用
- `d.instance_method()` — 实例方法从实例调用
- `Demo.static_method()` — 静态方法从类调用

## 12. 工厂方法与单例

**工厂方法 (类方法的经典用途)**:

```python
class Person:
    def __init__(self, name, birth_year):
        self.name = name
        self.birth_year = birth_year

    @classmethod
    def from_string(cls, s):     # 从字符串创建
        name, year = s.split(",")
        return cls(name, int(year))

    @classmethod
    def from_dict(cls, d):       # 从字典创建
        return cls(d["name"], d["birth_year"])

# 三种方式都调同一个 __init__
p1 = Person("Alice", 1990)
p2 = Person.from_string("Bob,1985")
p3 = Person.from_dict({"name": "Charlie", "birth_year": 2000})
```

**单例模式 (需要重写 __new__)**:

```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

s1 = Singleton()
s2 = Singleton()
s1 is s2  # True, 永远返回同一个实例
```

**继承不可变类型 (也需要重写 __new__)**:

```python
class UpperStr(str):
    def __new__(cls, value):
        return super().__new__(cls, value.upper())

UpperStr("hello")  # → "HELLO"
```

## 13. 内置工具函数

| 函数 | 作用 | 示例 |
|---|---|---|
| `type(obj)` | 查看对象的类 | `type(p)` → `<class 'Person'>` |
| `isinstance(obj, Class)` | 检查是否为实例 (支持继承链) | `isinstance(dog, Animal)` → True |
| `hasattr(obj, 'attr')` | 检查是否有某属性 | `hasattr(p, 'name')` → True |
| `getattr(obj, 'attr', default)` | 安全取属性值 | `getattr(p, 'email', '无')` → '无' |
| `setattr(obj, 'attr', val)` | 动态设置属性 | `setattr(p, 'name', 'Bob')` |
| `delattr(obj, 'attr')` | 动态删除属性 | 等价于 `del p.name` |

- `isinstance` 比 `type(obj) == Class` 更好, 因为会检查整条继承链
- `getattr(obj, name, default)` 比 `obj.name` 更安全, 不存在时返回默认值而不是抛异常

---

## 速查: 所有魔术方法

| 魔术方法 | 触发 | 用途 |
|---|---|---|
| `__init__(self)` | `obj = Class()` | 初始化对象 |
| `__new__(cls)` | `obj = Class()` | 创建对象 (__init__之前) |
| `__repr__(self)` | `repr(obj)` / print | 开发者字符串表示 |
| `__str__(self)` | `str(obj)` / print | 用户字符串表示 |
| `__eq__(self, o)` | `a == b` | 相等比较 |
| `__hash__(self)` | `hash(obj)` | 让对象可哈希 (放进set/dict key) |
| `__bool__(self)` | `bool(obj)` / if obj | 自定义真值判断 |
| `__len__(self)` | `len(obj)` | 返回长度 |
| `__call__(self)` | `obj()` | 让实例可调用 |

---

## 学习路径

```
01_class_basic.py     → 类, self, __init__, 类属性 vs 实例属性
02_inheritance.py     → 继承, 多态, super(), MRO, Mixin, ABC
03_encapsulation.py   → _/__ 约定, @property, setter/deleter
04_classmethod.py     → classmethod, staticmethod, __new__, 工厂方法
```
