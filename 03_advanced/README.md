# 进阶特性 (魔术方法) 笔记

## 目录

1. [迭代器协议](#1-迭代器协议-__iter__--__next__)
2. [上下文管理器](#2-上下文管理器-__enter__--__exit__)
3. [字符串表示](#3-字符串表示-__str__--__repr__)
4. [容器协议](#4-容器协议-__getitem__--__setitem__--__len__)
5. [可调用协议](#5-可调用协议-__call__)
6. [比较运算符](#6-比较运算符-__eq__--__lt__-等)
7. [数值运算符](#7-数值运算符-__add__--__mul__-等)
8. [装饰器](#8-装饰器)
9. [描述符协议](#9-描述符协议-__get__--__set__--__delete__)
10. [属性访问控制](#10-属性访问控制-__getattr__--__setattr__)
11. [生成器进阶](#11-生成器进阶-yield-from--send)
12. [异步编程基础](#12-异步编程基础-async--await)

---

## 文件映射

```
03_advanced/
├── 11_iterator.py           → 迭代器协议（__iter__ / __next__）
├── 12_context_manager.py    → 上下文管理器（__enter__ / __exit__）
├── 13_itertools.py          → itertools 迭代器工具集
├── 01_str_repr.py           → __str__ / __repr__
├── 02_container.py          → 容器协议
├── 03_callable.py           → __call__
├── 04_comparison.py         → 比较运算符
├── 05_numeric.py            → 数值运算符
├── 06_decorator.py          → 装饰器
├── 07_descriptor.py         → 描述符协议
├── 08_attribute_access.py   → 属性访问控制
├── 09_generator_advanced.py → 生成器进阶
├── 10_async_basics.py       → 异步编程基础
└── README.md                → 本文件
```

> `11_iterator.py`～`13_itertools.py` 编号排在最后：11/12 是协议基础（for / with 的底层），建议最先读；
> 13 是迭代器工具箱，读完 `09_generator_advanced.py` 再来看。

## 1. 迭代器协议 (`__iter__` / `__next__`)

**迭代器**: 一个能记住遍历位置的对象, 从第一个元素开始访问, 只能向前不能后退.

### 核心方法

| 方法             | 作用                                           |
| ---------------- | ---------------------------------------------- |
| `__iter__(self)` | 返回迭代器自身 (通常是 `return self`)          |
| `__next__(self)` | 返回下一个元素, 没有更多时抛出 `StopIteration` |

### for 循环的本质

```python
for x in obj:
    ...

# 等价于:
iterator = iter(obj)              # 1. 获取迭代器
while True:
    try:
        x = next(iterator)        # 2. 反复取下一个值
    except StopIteration:         # 3. 捕获 StopIteration 结束
        break
```

### 可迭代对象 vs 迭代器

|              | 可迭代对象                    | 迭代器                      |
| ------------ | ----------------------------- | --------------------------- |
| 实现         | `__iter__`                    | `__iter__` + `__next__`     |
| 能否多次遍历 | 是 (每次 iter() 返回新迭代器) | 否 (只能遍历一次)           |
| 例子         | list, tuple, dict, str        | 生成器, iter(list) 的返回值 |

---

## 2. 上下文管理器 (`__enter__` / `__exit__`)

**作用**: 确保资源在使用后被正确释放, 无论是否发生异常.

### 核心方法

| 方法                                  | 调用时机     | 返回值作用                           |
| ------------------------------------- | ------------ | ------------------------------------ |
| `__enter__()`                         | 进入 with 块 | 返回值赋给 `as` 后的变量             |
| `__exit__(exc_type, exc_val, exc_tb)` | 离开 with 块 | 返回 True 抑制异常, False 让异常传播 |

### with 语句的等价展开

```python
with expression as target:
    body

# 等价于:
manager = expression
target = manager.__enter__()
try:
    body
except:
    if not manager.__exit__(*sys.exc_info()):
        raise
else:
    manager.__exit__(None, None, None)
```

### 创建方式

| 方式                             | 适用场景                  |
| -------------------------------- | ------------------------- |
| 实现 `__enter__`/`__exit__` 的类 | 复杂逻辑                  |
| `@contextmanager` 装饰生成器     | 简单场景 (推荐)           |
| `contextlib.closing(obj)`        | 包裹只有 `close()` 的对象 |
| `contextlib.suppress(Error)`     | 忽略指定异常              |
| `contextlib.ExitStack`           | 动态管理多个上下文        |

---

## 3. 字符串表示 (`__str__` / `__repr__`)

**问题**: 默认 `print(obj)` 输出 `<__main__.Point object at 0x...>`, 毫无意义.

### 两者分工

|            | 目标读者      | 谁调用                   | 追求                         |
| ---------- | ------------- | ------------------------ | ---------------------------- |
| `__repr__` | 开发者 (自己) | `repr(obj)`, 交互环境    | 清晰无歧义, 最好能 eval 还原 |
| `__str__`  | 用户          | `str(obj)`, `print(obj)` | 好看易懂                     |

### 调用链路

```
print(obj) → str(obj) → __str__() → 没找到 → __repr__() → 都没找到 → 内存地址
repr(obj)  → __repr__() → 没找到 → 内存地址
```

**经验**: 至少实现 `__repr__`. 有了它就不会出现 `<object at 0x...>` 这种废输出.

### f-string 强制开关

```python
f"{obj}"     # 默认 __str__
f"{obj!s}"   # 强制 __str__
f"{obj!r}"   # 强制 __repr__ (调试时常用)
```

---

## 4. 容器协议 (`__getitem__` / `__setitem__` / `__len__`)

**作用**: 让自定义类像 list/dict 一样使用 `[]`, `len()`, `in`.

### 方法速查

| 语法             | 魔术方法                      | 说明              |
| ---------------- | ----------------------------- | ----------------- |
| `obj[key]`       | `__getitem__(self, key)`      | 根据 key 获取元素 |
| `obj[key] = val` | `__setitem__(self, key, val)` | 设置元素          |
| `del obj[key]`   | `__delitem__(self, key)`      | 删除元素          |
| `len(obj)`       | `__len__(self)`               | 返回元素个数      |
| `x in obj`       | `__contains__(self, x)`       | 检查包含关系      |

### 调用链路

```
obj[0]:
  type(obj).__getitem__(obj, 0)

len(obj):
  type(obj).__len__(obj)  ← CPython 优化: 直接读 C 层 ob_size, O(1)

x in obj:
  先找 __contains__ → 没找到用 __iter__ → 没找到用 __getitem__ 逐个尝试
```

### 可变 vs 不可变容器

|                              | 需要实现的方法                                         |
| ---------------------------- | ------------------------------------------------------ |
| 可变 (list/dict/set)         | `__getitem__`, `__setitem__`, `__delitem__`, `__len__` |
| 不可变 (tuple/str/frozenset) | `__getitem__`, `__len__`                               |

### 与迭代器的关系

- 容器: 有 `__getitem__` 或 `__iter__`, 能"被遍历"
- 迭代器: 有 `__next__` + `__iter__`, 能"去遍历"容器

for 循环查找顺序: `__iter__` > `__getitem__` (从 0 开始递增, 直到 IndexError)

---

## 5. 可调用协议 (`__call__`)

**作用**: 让实例像函数一样被调用 `obj()`. 本质是"带状态的函数".

### 可调用对象

```python
callable(print)           # True (函数)
callable(lambda x: x)     # True (lambda)
callable(Counter)         # True (类本身)
callable(counter)         # True (有 __call__ 的实例)
callable("hello")         # False
```

### 典型场景

| 场景         | 示例                                     |
| ------------ | ---------------------------------------- |
| 计数器       | `counter()` 而不是 `counter.increment()` |
| 带参函数工厂 | `add5(10)` 创建"加了固定数"的函数        |
| 缓存装饰器   | `memo(func)` 返回带缓存的可调用对象      |
| 策略模式     | `discount(price)` 所有策略同一调用方式   |
| 类装饰器     | 基于 `__call__`, 用属性保存状态          |

---

## 6. 比较运算符 (`__eq__` / `__lt__` 等)

**问题**: 默认 `==` 比较内存地址 (is), 而不是内容. `s1 == s2` 返回 False 尽管数据一样.

### 六个方法

| 魔术方法 | 符号 | 不实现时的默认行为     |
| -------- | ---- | ---------------------- |
| `__eq__` | `==` | 比较内存地址 (is)      |
| `__ne__` | `!=` | 自动取 `__eq__` 的反值 |
| `__lt__` | `<`  | 抛 TypeError           |
| `__le__` | `<=` | 抛 TypeError           |
| `__gt__` | `>`  | 抛 TypeError           |
| `__ge__` | `>=` | 抛 TypeError           |

### 偷懒技巧

```python
from functools import total_ordering

@total_ordering   # 只写 __eq__ + __lt__, 其他 4 个自动生成
class Student:
    def __eq__(self, other): ...
    def __lt__(self, other): ...
```

### == vs is

|            | `==`      | `is`            |
| ---------- | --------- | --------------- |
| 比较什么   | 值 (内容) | 身份 (内存地址) |
| 调用什么   | `__eq__`  | 不可重载        |
| 可否自定义 | 是        | 否              |

### NotImplemented

```python
def __eq__(self, other):
    if not isinstance(other, MyClass):
        return NotImplemented   # 返回这个让 Python 尝试 other.__eq__(self)
    return self.value == other.value
```

- `NotImplemented` (不是异常): 告诉 Python 换方案
- `NotImplementedError` (是异常): 子类没实现这个方法

---

## 7. 数值运算符 (`__add__` / `__mul__` 等)

### 三种运算符

| 类别                    | 魔术方法                                       | 语法                               |
| ----------------------- | ---------------------------------------------- | ---------------------------------- |
| 算术运算符 (返回新对象) | `__add__`, `__sub__`, `__mul__`, `__truediv__` | `a + b`, `a - b`, `a * b`, `a / b` |
| 增强赋值 (修改自身)     | `__iadd__`, `__isub__`, `__imul__`             | `a += b`, `a -= b`, `a *= b`       |
| 一元运算符              | `__neg__`, `__pos__`, `__abs__`                | `-a`, `+a`, `abs(a)`               |

### 右运算符 (**rXXX**)

```python
v * 3  ✓  Vector.__mul__(v, 3) → 能做
3 * v  ✗  int.__mul__(3, v) → NotImplemented
       → Vector.__rmul__(v, 3) → 能做
```

如果你希望类能和内置类型混合运算, `__rXXX__` 几乎是必须的.

### `__add__` vs `__iadd__`

|                | `__add__`       | `__iadd__`               |
| -------------- | --------------- | ------------------------ |
| 语法           | `a + b`         | `a += b`                 |
| 是否修改原对象 | 否 (返回新对象) | 是 (修改自身, 返回 self) |
| 没实现时       | 不存在          | 降级为 `a = a + b`       |

---

## 8. 装饰器

**本质**: 接收函数, 返回新函数的"高阶函数".

```python
@decorator
def func():
    ...

# 等价于:
func = decorator(func)
```

### 核心概念

- **函数是一等公民**: 可以赋值给变量, 作为参数传递, 作为返回值
- **闭包**: 内部函数"记住"外部函数的变量
- **洋葱模型**: `@timer @logger def foo` → 进入 timer → 进入 logger → foo → 退出 logger → 退出 timer

### 三种形式

| 形式                                    | 适用场景                       |
| --------------------------------------- | ------------------------------ |
| `@decorator`                            | 无参装饰器, 最简单             |
| `@decorator(args)`                      | 带参装饰器, 本质是"装饰器工厂" |
| 类装饰器 (`class Decorator + __call__`) | 用属性保存状态                 |

### @wraps

不加 `@wraps` 会导致原函数的 `__name__`, `__doc__` 等元信息丢失, 变成 `wrapper`.
每个装饰器的 `wrapper` 上都应该加 `@wraps(func)`.

### 常见用途

日志, 计时, 权限检查, 缓存, 重试, 输入验证

---

## 9. 描述符协议 (`__get__` / `__set__` / `__delete__`)

**描述符**: 控制"属性如何被访问"的对象. `@property` 的底层实现.

### 核心方法

| 方法                             | 调用时机   |
| -------------------------------- | ---------- |
| `__get__(self, instance, owner)` | 读取属性时 |
| `__set__(self, instance, value)` | 设置属性时 |
| `__delete__(self, instance)`     | 删除属性时 |

### 数据描述符 vs 非数据描述符

|              | 实现的方法                            | 查找优先级               |
| ------------ | ------------------------------------- | ------------------------ |
| 数据描述符   | `__get__` + `__set__` 或 `__delete__` | **高于** 实例 `__dict__` |
| 非数据描述符 | 只有 `__get__`                        | **低于** 实例 `__dict__` |

### 属性查找顺序

```
1. 数据描述符 → 2. 实例 __dict__ → 3. 非数据描述符 → 4. 类属性 → 5. __getattr__
```

### @property 的底层

`@property` 本质就是一个数据描述符: `property` 类实现了 `__get__` 和 `__set__`.

### 内置描述符

- `@property` — 方法伪装成属性
- `@classmethod` — 第一个参数是 cls
- `@staticmethod` — 不需要 self 或 cls
- `__slots__` — 用描述符替代 `__dict__` 节省内存

---

## 10. 属性访问控制 (`__getattr__` / `__setattr__`)

### 四个方法的触发时机

| 方法               | 触发时机                        | 危险性             |
| ------------------ | ------------------------------- | ------------------ |
| `__getattribute__` | **每次**访问属性都调用          | 极易无限递归, 慎用 |
| `__getattr__`      | 正常查找**失败后**才调用 (兜底) | 安全, 常用         |
| `__setattr__`      | 每次设置属性时调用              | 容易递归           |
| `__delattr__`      | 每次删除属性时调用              | 相对安全           |

### 防递归技巧

在这些方法内部绝对不要直接写 `self.xxx`, 要绕过拦截:

```python
object.__setattr__(self, name, value)   # 用父类方法
self.__dict__[name] = value             # 直接操作字典
```

### 适用场景

- `__getattr__`: 代理模式, 动态属性, API 包装
- `__setattr__`: 属性验证, 访问日志, 不可变对象
- `__delattr__`: 属性保护, 清理逻辑

---

## 11. 生成器进阶 (`yield from` / `send`)

### yield from 做三件事

1. **自动迭代**: `yield from iterable` ≈ `for x in iterable: yield x`
2. **双向通道**: 调用方的 `send()`/`throw()`/`close()` 透传给子生成器
3. **捕获返回值**: 子生成器 `return` 的值会被 `yield from` 捕获

### send() —— 双向通信

```python
value = yield output    # output 产出给调用方, value 从调用方接收
```

```
调用方 ──send(value)──→ yield (接收)
调用方 ←──yield value── yield (产出)
```

### 生成器的三大优势

1. **惰性计算**: 需要时才生产, 内存友好
2. **流水线**: 像 Unix 管道一样串联处理步骤
3. **协程**: send/throw/close 实现双向通信

### 生成器表达式 vs 列表推导式

|      | 列表推导式                 | 生成器表达式               |
| ---- | -------------------------- | -------------------------- |
| 语法 | `[x**2 for x in range(N)]` | `(x**2 for x in range(N))` |
| 内存 | 一次性生成所有元素         | 惰性, 几乎不占             |
| 适用 | 多次遍历, 随机访问         | 一次遍历, 数据量大         |

---

## 12. 异步编程基础 (`async` / `await`)

### 核心概念

| 概念                    | 解释                                   |
| ----------------------- | -------------------------------------- |
| coroutine (协程)        | `async def` 定义的函数, 调用不立即执行 |
| `await`                 | 等待协程完成, 交出控制权               |
| event loop (事件循环)   | 调度器, 轮流执行所有协程               |
| `asyncio.run()`         | 程序进入异步世界的入口                 |
| `asyncio.gather()`      | 并发执行多个协程                       |
| `asyncio.create_task()` | 把协程包装成 Task 放入事件循环         |

### 异步 != 多线程

- 异步: 单线程内切换任务 (并发)
- 多线程: 多个收银台同时工作 (并行)
- 适合: I/O 密集型 (网络, 数据库, 文件)
- 不适合: CPU 密集型 (计算, 图像处理)

### 异步版本的特殊方法

| 同步                     | 异步                       | 用途         |
| ------------------------ | -------------------------- | ------------ |
| `__iter__` / `__next__`  | `__aiter__` / `__anext__`  | `async for`  |
| `__enter__` / `__exit__` | `__aenter__` / `__aexit__` | `async with` |

### 常见误区

- "async 函数一定比同步快" → 错, 对单个任务反而有调度开销
- "await 让代码并行了" → 错, await 是在等, 只有 gather/create_task 才并发
- "asyncio.sleep() 和 time.sleep() 一样" → 错, asyncio.sleep 只挂起当前协程

---

## 速查: 全部魔术方法

| 协议         | 魔术方法                                                   | 触发语法                                   |
| ------------ | ---------------------------------------------------------- | ------------------------------------------ |
| 迭代器       | `__iter__`, `__next__`                                     | `for x in obj`                             |
| 上下文管理器 | `__enter__`, `__exit__`                                    | `with obj as x`                            |
| 字符串表示   | `__str__`, `__repr__`                                      | `print(obj)`, `repr(obj)`                  |
| 容器         | `__getitem__`, `__setitem__`, `__delitem__`                | `obj[key]`, `obj[key] = v`, `del obj[key]` |
| 容器         | `__len__`, `__contains__`                                  | `len(obj)`, `x in obj`                     |
| 可调用       | `__call__`                                                 | `obj()`                                    |
| 比较运算符   | `__eq__`, `__ne__`, `__lt__`, `__le__`, `__gt__`, `__ge__` | `==`, `!=`, `<`, `<=`, `>`, `>=`           |
| 数值运算符   | `__add__`, `__sub__`, `__mul__`, `__truediv__`             | `+`, `-`, `*`, `/`                         |
| 数值运算符   | `__iadd__`, `__isub__`                                     | `+=`, `-=`                                 |
| 一元运算符   | `__neg__`, `__pos__`, `__abs__`                            | `-obj`, `+obj`, `abs(obj)`                 |
| 描述符       | `__get__`, `__set__`, `__delete__`                         | 属性访问控制                               |
| 属性访问     | `__getattr__`, `__setattr__`, `__delattr__`                | 属性访问兜底                               |
| 生成器       | `yield`, `yield from`                                      | 生成器函数                                 |
| 异步         | `__aiter__`, `__anext__`, `__aenter__`, `__aexit__`        | `async for`, `async with`                  |

---
