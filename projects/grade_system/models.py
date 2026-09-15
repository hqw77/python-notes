"""
数据模型 —— Student 和 GradeManager

用到的知识:
  02_oop:    __init__, __str__, __repr__, @property
  03_advanced: __eq__ 按姓名判断相同, __lt__ 按成绩排序
  03_advanced: 容器协议 (__getitem__, __len__) 让 GradeManager 能被 for 遍历
"""

class Student:
    """学生: 姓名 + 多门成绩"""

    def __init__(self, name, scores=None):
        self.name = name
        self._scores = list(scores) if scores else []   # 内部存储用 _scores

    def add_score(self, score):
        """添加一个成绩"""
        if not isinstance(score, (int, float)):
            raise TypeError("成绩必须是数字")
        self._scores.append(score)

    # ---------- 属性访问 ----------
    @property
    def scores(self):
        """返回成绩列表 (只读)"""
        return self._scores.copy()            # 返回副本, 防止外部直接修改内部列表

    @property
    def average(self):
        """计算属性: 平均分 (没有 setter = 只读)"""
        if not self._scores:
            return 0
        return sum(self._scores) / len(self._scores)

    @property
    def total(self):
        """总分"""
        return sum(self._scores)

    # ---------- 字符串表示 ----------
    def __str__(self):
        """给用户看的: print(student) 时调用"""
        return f"{self.name} | 成绩: {self._scores} | 平均: {self.average:.1f}"

    def __repr__(self):
        """给开发者看的: 调试时显示"""
        return f"Student({self.name!r}, {self._scores!r})"

    # ---------- 比较运算符 ----------
    def __eq__(self, other):
        """同名学生视为同一个学生"""
        if not isinstance(other, Student):
            return NotImplemented
        return self.name == other.name

    def __lt__(self, other):
        """按平均分排序 (从低到高)"""
        if not isinstance(other, Student):
            return NotImplemented
        return self.average < other.average

    def __hash__(self):
        """有 __eq__ 必须配 __hash__, 否则不能放进 set"""
        return hash(self.name)


class GradeManager:
    """班级成绩管理器 —— 是一个容器, 能 for 遍历, 能用 [] 取学生"""

    def __init__(self, name="默认班级"):
        self.class_name = name
        self._students = []       # 内部用列表存储学生对象

    # ---------- 容器协议 ----------
    def __getitem__(self, index):
        """manager[0] 或 manager[0:3] 切片"""
        return self._students[index]

    def __len__(self):
        """len(manager) → 学生人数"""
        return len(self._students)

    def __contains__(self, student):
        """name in manager → 检查名字是否已在班级里"""
        return student in self._students

    # ---------- 增删查 ----------
    def add(self, student):
        """添加学生, 同名会报错"""
        if student in self._students:
            raise ValueError(f"学生 '{student.name}' 已存在")
        self._students.append(student)

    def remove(self, name):
        """按名字删除学生"""
        for i, s in enumerate(self._students):
            if s.name == name:
                del self._students[i]
                return s
        raise KeyError(f"没有叫 '{name}' 的学生")
    # raise  手动触发（抛出）异常的关键字

    def find(self, name):
        """按名字查找, 返回 Student 或 None"""
        for s in self._students:
            if s.name == name:
                return s
        return None

    # ---------- 筛选与排序 ----------
    def filter_passed(self):
        """用列表推导式筛选及格学生 (平均 >= 60)"""
        return [s for s in self._students if s.average >= 60]

    def filter_failed(self):
        """用生成器表达式筛选不及格学生 (平均 < 60)"""
        return (s for s in self._students if s.average < 60)

    def rank(self, reverse=True):
        """排名: 用 sorted() + __lt__ 排序, 不修改原列表"""
        return sorted(self._students, reverse=reverse)

    def top_n(self, n=3):
        """前 N 名"""
        return self.rank()[:n]

    # ---------- 统计 ----------
    @property
    def class_average(self):
        """全班平均分"""
        if not self._students:
            return 0
        return sum(s.average for s in self._students) / len(self._students)

    def summary(self):
        """班级概况"""
        return (
            f"班级: {self.class_name}\n"
            f"  人数: {len(self)}, 全班平均: {self.class_average:.1f}\n"
            f"  最高分: {self.top_n(1)[0] if self._students else '无'}\n"
            f"  及格人数: {len(self.filter_passed())}"
        )
