"""
比较运算符协议 —— __eq__ / __ne__ / __lt__ / __le__ / __gt__ / __ge__

【问题场景】

  class Student:
      def __init__(self, name, score):
          self.name = name
          self.score = score

  s1 = Student("Alice", 90)
  s2 = Student("Alice", 90)

  print(s1 == s2)  # False !!! 明明数据一样，为什么不等？

  因为默认的 == 比较的是内存地址(is 判断），而不是内容。
  要实现"按内容比较"，你需要写 __eq__。

  同理,sorted([s1, s2, s3]) 要能排序，需要写 __lt__(小于)。

【六个方法的完整表格】

  ┌──────────┬──────┬────────────────────────┬──────────────────────┐
  │ 魔术方法  │ 符号  │ 含义                    │ 不实现时的默认行为    │
  ├──────────┼──────┼────────────────────────┼──────────────────────┤
  │ __eq__   │ ==   │ 相等                    │ 比较内存地址（is）     │
  │ __ne__   │ !=   │ 不等                    │ 自动取 __eq__ 的反值   │
  │ __lt__   │ <    │ 小于（less than）        │ 抛 TypeError          │
  │ __le__   │ <=   │ 小于等于（less equal）    │ 抛 TypeError          │
  │ __gt__   │ >    │ 大于（greater than）     │ 抛 TypeError          │
  │ __ge__   │ >=   │ 大于等于（greater equal） │ 抛 TypeError          │
  └──────────┴──────┴────────────────────────┴──────────────────────┘

【调用链路 —— sorted() 是怎么比较的？】

  sorted([a, b, c]) 默认从小到大排序，内部调用 a.__lt__(b)。
  如果 a.__lt__(b) 返回 True，a 排在 b 前面。

  Python 的排序算法（Timsort）只会调用 __lt__，不会调用 __gt__ 或 __ge__。
  但 max() 可能用 __gt__，所以建议至少实现 __eq__ + __lt__。

【省力技巧：@total_ordering】

  from functools import total_ordering

  @total_ordering
  class Student:
      def __eq__(self, other): ...   # 只写这个
      def __lt__(self, other): ...   # + 这个

  剩下 4 个（__ne__, __le__, __gt__, __ge__）自动生成。
  原理：装饰器通过组合 __eq__ 和 __lt__ 推断出其他比较方法。

【Python 特有的链式比较】

  a < b < c  等价于  a < b and b < c  （但 b 只计算一次）
  这是 Python 语法层面的支持，和魔术方法无关，但比较运算符是用得上的。

【== vs is 的区别】

  ==  : 比较"值"是否相等 → 调用 __eq__,默认比较内存地址
  is  : 比较"身份"是否相同 → 就是比较内存地址，不能重载

  所以：
    a == b   → 内容相同（你定义的 "相等"）
    a is b   → 就是同一个对象（id(a) == id(b)）

  例：
    a = [1, 2, 3]
    b = [1, 2, 3]
    a == b  # True  — 内容相同
    a is b  # False — 不是同一个对象

【NotImplemented vs NotImplementedError】

  NotImplemented（不是异常！）：告诉 Python"我不知道怎么和这个类型比较"
    → Python 会尝试交换操作数
  NotImplementedError（是异常）：子类没实现这个方法

  在你的 __eq__ 里，遇到不认识的类型应该 return NotImplemented，
  而不是 raise NotImplementedError。
"""

from functools import total_ordering

# ============================================================
# 1. 基础：实现 == 比较
# ============================================================
class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def __eq__(self, other):
        """self == other 时调用"""
        if not isinstance(other, Student):
            return NotImplemented   # 返回 NotImplemented 让 Python 尝试 other.__eq__(self)
        return self.name == other.name and self.score == other.score

    def __repr__(self):
        return f"Student({self.name!r}, {self.score})"

s1 = Student("Alice", 90)
s2 = Student("Alice", 90)
s3 = Student("Bob", 85)

print("--- 基础相等比较 ---")
print(f"  s1 == s2: {s1 == s2}")     # True —— 数据相同
print(f"  s1 == s3: {s1 == s3}")     # False

# 没有 __eq__ 时，== 比较的是内存地址（is）
# 有了 __eq__，== 比较的是你定义的逻辑


# ============================================================
# 2. 排序比较 —— 谁成绩更高？
# ============================================================
class StudentV2:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def __eq__(self, other):
        if not isinstance(other, StudentV2):
            return NotImplemented
        return self.score == other.score

    def __lt__(self, other):
        """self < other —— 小于"""
        if not isinstance(other, StudentV2):
            return NotImplemented
        return self.score < other.score

    def __le__(self, other):
        """self <= other —— 小于等于"""
        if not isinstance(other, StudentV2):
            return NotImplemented
        return self.score <= other.score

    def __gt__(self, other):
        """self > other —— 大于"""
        if not isinstance(other, StudentV2):
            return NotImplemented
        return self.score > other.score

    def __ge__(self, other):
        """self >= other —— 大于等于"""
        if not isinstance(other, StudentV2):
            return NotImplemented
        return self.score >= other.score

    def __repr__(self):
        return f"StudentV2({self.name!r}, {self.score})"

students = [
    StudentV2("Alice", 90),
    StudentV2("Bob", 85),
    StudentV2("Charlie", 95),
]
print(f"\n--- 排序比较 ---")
print(f"  排序前: {students}")
print(f"  按成绩排序后: {sorted(students)}")         # sorted() 内部用 __lt__
print(f"  最高分: {max(students)}")                   # max() 也用比较方法
print(f"  Alice > Bob: {students[0] > students[1]}")


# ============================================================
# 3. @total_ordering —— 偷懒写法，只写两个方法
# ============================================================
@total_ordering
class StudentV3:
    """只写了 __eq__ 和 __lt__，其他比较方法自动生成"""
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def __eq__(self, other):
        if not isinstance(other, StudentV3):
            return NotImplemented
        return self.score == other.score

    def __lt__(self, other):
        if not isinstance(other, StudentV3):
            return NotImplemented
        return self.score < other.score

    def __repr__(self):
        return f"StudentV3({self.name!r}, {self.score})"

a, b = StudentV3("A", 80), StudentV3("B", 90)
print(f"\n--- @total_ordering 自动生成 ---")
print(f"  a == b: {a == b}")    # 你写的 __eq__
print(f"  a < b:  {a < b}")     # 你写的 __lt__
print(f"  a > b:  {a > b}")     # 自动生成
print(f"  a <= b: {a <= b}")    # 自动生成
print(f"  a >= b: {a >= b}")    # 自动生成
print(f"  a != b: {a != b}")    # 自动生成（__eq__ 的反值）


# ============================================================
# 4. 链式比较 (Python 特有)
# ============================================================
# a < b < c  等价于  a < b and b < c（但 b 只计算一次）
print(f"\n--- 链式比较 ---")
score = 85
print(f"  60 < score < 100: {60 < score < 100}")     # True


# ============================================================
# 5. 实用案例：版本号比较
# ============================================================
@total_ordering
class Version:
    """语义化版本号，支持比较"""
    def __init__(self, version_str):
        parts = version_str.split(".")
        self.major, self.minor, self.patch = map(int, parts)

    def __eq__(self, other):
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __lt__(self, other):
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __repr__(self):
        return f"v{self.major}.{self.minor}.{self.patch}"

print(f"\n--- 版本号比较 ---")
v1, v2, v3 = Version("1.2.3"), Version("1.10.0"), Version("2.0.0")
print(f"  {v1} < {v2}: {v1 < v2}")    # True
print(f"  {v2} < {v3}: {v2 < v3}")    # True
print(f"  排序: {sorted([v3, v1, v2])}")


# ============================================================
# 6. NotImplemented vs NotImplementedError
# ============================================================
# NotImplemented（不是异常）: 返回给 Python 说"我不会处理这个类型"
#   → Python 会尝试交换操作数，调 other.__eq__(self)
# NotImplementedError（是异常）: 表示子类还没有实现这个方法
print(f"\n--- NotImplemented 的作用 ---")

class IntWrapper:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, IntWrapper):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        return NotImplemented     # 告诉 Python "我处理不了，你试试别的"

w = IntWrapper(5)
print(f"  w == IntWrapper(5): {w == IntWrapper(5)}")   # True
print(f"  w == 5: {w == 5}")                           # True（Python 自动处理）


# ============================================================
# 总结
# ============================================================
# - __eq__: == （最常用，必须实现）
# - __ne__: != （不写就自动取反）
# - __lt__: <, __le__: <=, __gt__: >, __ge__: >=
# - @total_ordering: 只写 __eq__ + 一个，其他自动生成
# - NotImplemented: 告诉 Python 换方案，NotImplementedError: 抛异常
# - dataclass 和 namedtuple 也会自动生成比较方法
