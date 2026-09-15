"""测试 models.py —— 运行: pytest tests/ -v"""

# 把 models 加到 path, 让测试文件能找到它
import sys
sys.path.insert(0, "..")

from models import Student, GradeManager
import pytest


# --- 测试 Student ---

def test_student_create():
    s = Student("张三", [85, 90])
    assert s.name == "张三"
    assert s.scores == [85, 90]
    assert s.average == 87.5


def test_student_add_score():
    s = Student("张三")
    s.add_score(85)
    s.add_score(90)
    assert s.average == 87.5


def test_student_eq():
    s1 = Student("张三", [85, 90])
    s2 = Student("张三", [50, 60])   # 同名
    s3 = Student("李四", [85, 90])   # 不同名
    assert s1 == s2
    assert s1 != s3


def test_student_lt():
    s1 = Student("高分", [90, 95])
    s2 = Student("低分", [60, 65])
    assert s2 < s1


def test_student_str():
    s = Student("张三", [85, 90])
    assert "张三" in str(s)
    assert "87.5" in str(s)


# --- 测试 GradeManager ---

def test_add_and_get():
    m = GradeManager()
    m.add(Student("张三", [85, 90]))
    assert len(m) == 1
    assert m[0].name == "张三"


def test_add_duplicate():
    m = GradeManager()
    m.add(Student("张三"))
    with pytest.raises(ValueError):
        m.add(Student("张三"))


def test_remove():
    m = GradeManager()
    m.add(Student("张三"))
    m.remove("张三")
    assert len(m) == 0


def test_remove_not_found():
    m = GradeManager()
    with pytest.raises(KeyError):
        m.remove("不存在")


def test_filter():
    m = GradeManager()
    m.add(Student("及格", [80, 90]))
    m.add(Student("不及格", [50, 60]))
    assert len(m.filter_passed()) == 1
    assert len(list(m.filter_failed())) == 1


def test_rank():
    m = GradeManager()
    m.add(Student("中", [70, 80]))
    m.add(Student("高", [90, 95]))
    m.add(Student("低", [50, 60]))
    ranked = m.rank(reverse=True)
    assert ranked[0].name == "高"
    assert ranked[2].name == "低"


@pytest.fixture
def sample_manager():
    """预置了 3 个学生的班级"""
    m = GradeManager("测试班")
    m.add(Student("张三", [85, 90]))
    m.add(Student("李四", [92, 88]))
    m.add(Student("王五", [60, 55]))
    return m

def test_fixture_len(sample_manager):
    assert len(sample_manager) == 3

def test_fixture_average(sample_manager):
    assert sample_manager.class_average > 0


@pytest.mark.parametrize("scores, expected_avg", [
    ([85, 90, 78], 84.3),
    ([100, 0], 50.0),
    ([], 0),
    ([60], 60.0),
])
def test_average_parametrize(scores, expected_avg):
    s = Student("测试", scores)
    assert abs(s.average - expected_avg) < 0.1
