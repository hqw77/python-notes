"""
with 语句 —— 上下文管理器 (Context Manager)

with 语句用于简化资源管理，确保资源在使用后被正确释放。
它的核心价值是：无论代码块是否发生异常，都会执行清理操作。

典型场景：
- 文件操作（自动关闭文件）
- 锁的获取与释放
- 数据库连接管理
- 网络连接管理
- 临时状态恢复

【运行方式】
  全部: python with.py
  单个: python with.py basic / protocol / flow / timer / temp_attr / lock / contextlib / nested / exit_control / async
"""

import time
import threading
from contextlib import contextmanager, ContextDecorator, suppress, ExitStack


# ============================================================
# 1. 基本用法 —— 文件操作（最常见的例子）
# ============================================================
def demo_basic():
    # 不加 with —— 需要手动 close，异常时可能忘记关闭
    f = open("test.txt", "w")
    try:
        f.write("hello")
    finally:
        f.close()                     # 必须手动关闭

    # 加了 with —— 自动关闭，简洁安全
    with open("test.txt", "w") as f:
        f.write("hello")
    # 离开 with 块时，文件自动关闭，即使发生了异常也会关闭


# ============================================================
# 2. 上下文管理器协议：__enter__ 和 __exit__
# ============================================================
def demo_protocol():
    # __enter__: 进入 with 块时调用，返回值赋给 as 后面的变量
    # __exit__:  离开 with 块时调用，负责清理工作

    class MyContextManager:
        """自定义上下文管理器示例"""
        def __enter__(self):
            print(">>> 进入上下文")
            return "这是资源"         # 返回值赋给 as 后面的变量

        def __exit__(self, exc_type, exc_val, _exc_tb):
            # 三个参数：异常类型、异常值、traceback
            # 如果没有异常发生，三个参数都是 None
            if exc_type:
                print(f">>> 退出上下文（发生异常: {exc_type.__name__}: {exc_val}）")
            else:
                print(">>> 退出上下文（无异常）")
            # 返回 True 会抑制异常（吞掉异常，不向上传播）
            # 返回 False/None 则异常正常传播
            return False

    print("--- 正常情况 ---")
    with MyContextManager() as resource:
        print(f"  使用中: {resource}")

    print("\n--- 发生异常 ---")
    try:
        with MyContextManager() as resource:
            print(f"  使用中: {resource}")
            raise ValueError("出错了")
    except ValueError:
        print("  外部捕获到了异常")


# ============================================================
# 3. with 语句的执行流程（底层原理）
# ============================================================
def demo_flow():
    """
    with expression as target:
        body

    等价于：

    manager = expression           # 1. 对表达式求值，得到上下文管理器对象
    target = manager.__enter__()   # 2. 调用 __enter__，返回值赋给 target
    try:
        body                       # 3. 执行 with 块内的代码
    except:
        #  4. 如果发生异常，调用 __exit__ 并传入异常信息
        if not manager.__exit__(exc_type, exc_val, exc_tb):
            raise                  # 如果 __exit__ 返回 False，重新抛出异常
    else:
        manager.__exit__(None, None, None)  # 5. 无异常时也调用 __exit__
    """


# ============================================================
# 4. 实用案例一：计时器
# ============================================================
def demo_timer():
    class Timer:
        """测量代码块执行时间的上下文管理器"""
        def __enter__(self):
            # time.perf_counter() → 高精度性能计时器（单位秒），适合测量代码耗时
            self.start = time.perf_counter()
            return self             # 返回自身，方便在 with 块内获取时间信息

        def __exit__(self, _exc_type, _exc_val, _exc_tb):
            self.end = time.perf_counter()
            self.elapsed = self.end - self.start
            print(f"  耗时: {self.elapsed:.6f} 秒")
            return False

    print("\n--- 计时器 ---")
    with Timer():
        total = sum(range(10_000_000))


# ============================================================
# 5. 实用案例二：状态暂存与恢复
# ============================================================
def demo_temp_attr():
    class TempAttr:
        """临时修改对象属性，离开 with 块时自动恢复"""
        def __init__(self, obj, attr, temp_value):
            self.obj = obj
            self.attr = attr
            self.temp_value = temp_value

        def __enter__(self):
            # getattr(对象, 属性名字符串[, 默认值]) → 读取对象的指定属性
            # 例: getattr(p, "name", None) 等价于 p.name，但属性名不存在时返回 None 而不报错
            self.original = getattr(self.obj, self.attr, None)
            # setattr(对象, 属性名字符串, 值) → 设置对象的属性，等价于 obj.attr = value
            setattr(self.obj, self.attr, self.temp_value)
            return self.obj

        def __exit__(self, _exc_type, _exc_val, _exc_tb):
            # setattr(p, "name", self.original) → 恢复原始值
            setattr(self.obj, self.attr, self.original)
            return False

    class Person:
        name = "张三"

    p = Person()
    print(f"\n  原始 name: {p.name}")
    with TempAttr(p, "name", "李四"):
        print(f"  with 块内: {p.name}")
    print(f"  恢复后: {p.name}")


# ============================================================
# 6. 实用案例三：锁管理（线程安全）
# ============================================================
def demo_lock():
    lock = threading.Lock()

    # 错误写法 —— 万一异常，锁永远不会释放
    # lock.acquire()
    # do_something()
    # lock.release()

    # 正确写法 —— with 保证锁一定释放
    # with lock:
    #     do_something()


# ============================================================
# 7. contextlib 模块 —— 更简洁的创建方式
# ============================================================
def demo_contextlib():
    # 方式一：@contextmanager 装饰器（把生成器函数变成上下文管理器）
    # @contextmanager 原理: 把函数中 yield 之前的代码当 __enter__, yield 后的代码当 __exit__
    # yield 抛出的值会赋给 with ... as 后面的变量
    @contextmanager
    def managed_file(filename, mode):
        """用 contextmanager 创建的文件上下文管理器"""
        f = open(filename, mode)
        try:
            # yield 之前 = __enter__：打开文件 → yield 把文件对象传给 as 后的变量
            yield f
        finally:
            # yield 之后 = __exit__：离开 with 块时执行，关闭文件
            f.close()

    print("\n--- contextmanager 装饰器 ---")
    with managed_file("test.txt", "w") as f:
        f.write("用 contextmanager 写文件")


    # 方式二：contextlib.closing —— 包裹只有 close() 方法的对象
    # from contextlib import closing
    # from urllib.request import urlopen
    # 对于有 close() 方法但没有 __enter__/__exit__ 的对象
    # with closing(urlopen("http://www.example.com")) as response:
    #     html = response.read()


    # 方式三：contextlib.ContextDecorator —— 既是上下文管理器又是装饰器
    # 继承 ContextDecorator 后，类的实例既可以当 with 用，也可以当 @装饰器 用
    class LogContext(ContextDecorator):
        """既可以当 with 用，也可以当装饰器用"""
        def __enter__(self):
            print("  [LOG] 开始")
            return self

        def __exit__(self, _exc_type, _exc_val, _exc_tb):
            print("  [LOG] 结束")
            return False

    print("\n--- ContextDecorator 用法 ---")
    print("1. 作为 with 语句:")
    with LogContext():
        print("    工作中的代码...")

    @LogContext()
    def my_function():
        print("    函数体中的代码...")

    print("\n2. 作为装饰器:")
    my_function()


    # 方式四：contextlib.suppress(异常类型) —— 忽略 with 块中发生的指定异常，程序不报错继续执行
    print("\n--- suppress 忽略异常 ---")
    with suppress(ZeroDivisionError):
        result = 1 / 0              # 不会抛异常，安静跳过
        print("这行不会执行")

    # 方式五：contextlib.ExitStack —— 动态管理数量不定的上下文管理器
    # ExitStack 像一个可以"注册"多个上下文管理器的容器，退出时按注册的逆序全部关闭
    # stack.enter_context() → 进入一个上下文管理器并注册到栈中，返回其 __enter__ 的返回值
    print("\n--- ExitStack 动态管理 ---")
    def process_files(filenames):
        with ExitStack() as stack:
            # stack.enter_context(open(fname, "w")) 打开文件并注册，退出时自动关闭所有文件
            files = [stack.enter_context(open(fname, "w"))
                     for fname in filenames]
            for i, f in enumerate(files):
                f.write(f"文件 {i}")
            # 所有文件自动关闭，即使中途出错


# ============================================================
# 8. 嵌套上下文管理器
# ============================================================
def demo_nested():
    print("\n--- 嵌套上下文 ---")

    # 写法一：多层 with
    with open("a.txt", "w") as fa:
        with open("b.txt", "w") as fb:
            fa.write("a")
            fb.write("b")

    # 写法二：单行多个（Python 3.1+）
    with open("a.txt", "w") as fa, open("b.txt", "w") as fb:
        fa.write("a2")
        fb.write("b2")

    # 写法三：传递已打开的文件
    with open("in.txt", "w") as fin:
        fin.write("data")
    with open("in.txt") as fin, open("out.txt", "w") as fout:
        fout.write(fin.read())


# ============================================================
# 9. __exit__ 的返回值控制异常传播
# ============================================================
def demo_exit_control():
    print("\n--- 控制异常传播 ---")

    class SuppressError:
        """吞掉指定类型的异常"""
        def __init__(self, error_type):
            self.error_type = error_type

        def __enter__(self):
            return self

        def __exit__(self, exc_type, _exc_val, _exc_tb):
            # issubclass(A, B) → 判断 A 是不是 B 的子类
            # 返回 True = 抑制异常（吞掉），False = 异常继续向外传播
            return exc_type is not None and issubclass(exc_type, self.error_type)

    print("  异常被吞掉的情况：")
    with SuppressError(ValueError):
        raise ValueError("这个异常不会传播出去")
    print("  正常到达这里")

    print("\n  异常不被吞掉的情况：")
    try:
        with SuppressError(TypeError):
            raise ValueError("这个异常会传播出去")
    except ValueError:
        print("  外部捕获到了 ValueError")


# ============================================================
# 10. 异步上下文管理器（Python 3.5+）
# ============================================================
def demo_async():
    """
    异步版本使用 __aenter__ 和 __aexit__：
        async with async_context_manager as resource:
            await resource.do_something()

    标准库示例：
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
    """


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "basic": demo_basic,
        "protocol": demo_protocol,
        "flow": demo_flow,
        "timer": demo_timer,
        "temp_attr": demo_temp_attr,
        "lock": demo_lock,
        "contextlib": demo_contextlib,
        "nested": demo_nested,
        "exit_control": demo_exit_control,
        "async": demo_async,
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
# 核心协议:
#   __enter__()       进入上下文，返回资源
#   __exit__(t, v, tb) 退出上下文，处理清理和异常
#
# 创建方式:
#   1. 实现 __enter__/__exit__ 的类
#   2. @contextmanager 装饰生成器函数（推荐，最简洁）
#   3. contextlib.ContextDecorator（可作为装饰器）
#
# 常用标准库:
#   with open(...)                 文件操作
#   with lock                      线程锁
#   with suppress(Error)           忽略指定异常
#   with ExitStack()               动态管理多个上下文
#   with closing(obj)              包裹只有 close() 的对象
#
# 关键点:
#   - with 保证 __exit__ 一定会被调用（哪怕发生异常）
#   - __exit__ 返回 True 会吞掉异常
#   - 多个上下文可以用逗号分隔写在一行
