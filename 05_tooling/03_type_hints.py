"""
类型注解 (Type Hints) -- 让代码有"说明书"

[什么是类型注解?]

  类型注解就是在写代码时标注变量和函数参数的类型.
  Python 运行时完全忽略它们, 但 IDE 和静态检查器 (mypy/pyright) 会利用它们.
  相当于给代码写了份类型说明书.

[为什么用类型注解?]

  1. IDE 自动补全更准: 知道变量类型才能给出正确提示
  2. 提前发现错误: 类型检查器在你运行之前就能发现 type mismatch
  3. 文档作用: 看到函数签名就知道参数应该传什么, 不用读源码

[类型注解不影响运行时!]

  x: int = "hello"    # Python 不会报错, 类型注解只是"建议"
  但 mypy 会报: error: Incompatible types in assignment

[运行方式]
  全部: python 03_type_hints.py
  单个: python 03_type_hints.py basic_types / containers / optional_union / any / callable / typevar / typeddict / literal / final / grade_system / mypy
"""

from typing import Any, Callable, Final, Literal, TypeVar, TypedDict

# ============================================================
# 1. 基本类型注解
# ============================================================
def demo_basic_types():
    # 变量注解
    name: str = "Alice"
    age: int = 30
    score: float = 92.5
    is_active: bool = True

    # 函数参数和返回值
    def greet(name: str) -> str:
        """参数是 str, 返回也是 str"""
        return f"Hello, {name}!"

    def add(a: int, b: int) -> int:
        return a + b

    def divide(a: float, b: float) -> float:
        if b == 0:
            return 0.0
        return a / b


# ============================================================
# 2. 容器类型 (Python 3.9+)
# ============================================================
def demo_containers():
    # list 里装 int
    scores: list[int] = [85, 90, 78]

    # dict 里 key 是 str, value 是 int
    student_map: dict[str, int] = {"张三": 85, "李四": 90}

    # tuple 前两个是 str, 最后一个是 float
    record: tuple[str, str, float] = ("张三", "2024-06-20", 92.5)

    # set 里装 str
    names: set[str] = {"张三", "李四", "王五"}

    # 函数参数用容器
    def average(scores: list[int]) -> float:
        if not scores:
            return 0.0
        return sum(scores) / len(scores)

    def find_student(name: str, data: dict[str, int]) -> int | None:
        """返回分数或 None"""
        return data.get(name)


# ============================================================
# 3. Optional 和 Union (Python 3.10+ 用 | 写法)
# ============================================================
def demo_optional_union():
    # Python 3.10+: X | Y 代替 Union[X, Y], X | None 代替 Optional[X]
    def get_score(name: str) -> int | None:     # 可能返回 int, 也可能返回 None
        if name == "张三":
            return 90
        return None

    def process(value: int | str) -> str:       # 参数可以是 int 或 str
        return str(value)

    # 旧写法 (3.9 及以前):
    # from typing import Optional, Union
    # def get_score(name: str) -> Optional[int]:
    # def process(value: Union[int, str]) -> str:


# ============================================================
# 4. Any -- 任意类型
# ============================================================
def demo_any():
    def debug_print(obj: Any) -> None:
        """接受任何类型的参数"""
        print(f"DEBUG: {obj!r}")


# ============================================================
# 5. Callable -- 函数类型
# ============================================================
def demo_callable():
    # 接受一个函数 f, 它接收 int 返回 int
    def apply(func: Callable[[int], int], x: int) -> int:
        return func(x)

    def square(n: int) -> int:
        return n * n

    apply(square, 5)    # → 25


# ============================================================
# 6. TypeVar -- 泛型
# ============================================================
def demo_typevar():
    T = TypeVar("T")   # T 可以是任何类型

    def first(items: list[T]) -> T:
        """返回列表第一个元素, 保持类型信息"""
        return items[0]

    first([1, 2, 3])       # 返回 int
    first(["a", "b", "c"]) # 返回 str


# ============================================================
# 7. TypedDict -- 有类型约束的字典
# ============================================================
def demo_typeddict():
    class StudentDict(TypedDict):
        """描述一个学生字典的结构"""
        name: str
        age: int
        scores: list[int]

    def process_student(d: StudentDict) -> float:
        return sum(d["scores"]) / len(d["scores"])


# ============================================================
# 8. Literal -- 限定为特定值
# ============================================================
def demo_literal():
    def set_log_level(level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]) -> None:
        """level 只能是这 4 个值之一, 传别的 mypy 会报错"""
        print(f"设置日志级别为 {level}")

    set_log_level("INFO")    # 合法
    # set_log_level("NONE")  # mypy 报错: 不在 Literal 列表中


# ============================================================
# 9. Final -- 常量标记
# ============================================================
def demo_final():
    MAX_SIZE: Final = 1024       # 标记后不能重新赋值 (仅静态检查, 运行时不管)
    PI: Final[float] = 3.14159


# ============================================================
# 10. 给成绩系统加类型注解 (实战)
# ============================================================
def demo_grade_system():
    # 改造后的 Student:
    class Student:
        def __init__(self, name: str, scores: list[int] | None = None) -> None:
            self.name: str = name
            self._scores: list[int] = list(scores) if scores else []

        def add_score(self, score: int | float) -> None:
            if not isinstance(score, (int, float)):
                raise TypeError("成绩必须是数字")
            self._scores.append(int(score))

        @property
        def scores(self) -> list[int]:
            return self._scores.copy()

        @property
        def average(self) -> float:
            if not self._scores:
                return 0.0
            return sum(self._scores) / len(self._scores)

        def __str__(self) -> str:
            return f"{self.name} | 成绩: {self._scores} | 平均: {self.average:.1f}"


    # 改造后的 GradeManager:
    class GradeManager:
        def __init__(self, name: str = "默认班级") -> None:
            self.class_name: str = name
            self._students: list[Student] = []

        def __getitem__(self, index: int) -> Student:
            return self._students[index]

        def __len__(self) -> int:
            return len(self._students)

        def add(self, student: Student) -> None:
            if student in self._students:
                raise ValueError(f"学生 '{student.name}' 已存在")
            self._students.append(student)

        def find(self, name: str) -> Student | None:
            for s in self._students:
                if s.name == name:
                    return s
            return None

        def filter_passed(self) -> list[Student]:
            return [s for s in self._students if s.average >= 60]

        @property
        def class_average(self) -> float:
            if not self._students:
                return 0.0
            return sum(s.average for s in self._students) / len(self._students)


# ============================================================
# 11. 静态类型检查: mypy
# ============================================================
def demo_mypy():
    # 安装: pip install mypy
    # 运行: mypy models.py   (检查 models.py 的类型)
    #
    # mypy 会检查:
    #   - 参数类型对不对
    #   - 返回值类型对不对
    #   - Optional 值有没有判 None
    #   - 等等
    #
    # VS Code 里的 Pylance/Pyright 也能做同样的事, 实时在编辑器显示红色波浪线
    pass


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "basic_types": demo_basic_types,
        "containers": demo_containers,
        "optional_union": demo_optional_union,
        "any": demo_any,
        "callable": demo_callable,
        "typevar": demo_typevar,
        "typeddict": demo_typeddict,
        "literal": demo_literal,
        "final": demo_final,
        "grade_system": demo_grade_system,
        "mypy": demo_mypy,
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
# - 类型注解是"说明书", 不影响运行时
# - ID 自动补全靠它, mypy 静态检查靠它
# - int, str, float, bool, None → 基本类型
# - list[int], dict[str, int] → 容器类型 (3.9+)
# - X | None → Optional (3.10+)
# - TypeVar → 泛型; TypedDict → 字典结构; Literal → 限定值
# - 库代码强烈建议加类型注解, 小脚本随意
