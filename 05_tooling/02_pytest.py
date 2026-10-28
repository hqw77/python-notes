"""
单元测试 (pytest) —— 让代码修改有底气

【什么是测试? 为什么要测试?】

  测试就是写代码来验证你的代码对不对.
  没有测试改了代码 → 不知道改了哪里 → 上线炸了 → 加班修
  有测试改了代码 → 跑一下 → 红了马上知道哪里坏了 → 下班回家

  Python 有两种测试框架:
    - unittest: 内置, 模仿 Java 的 JUnit, 啰嗦
    - pytest: 第三方, 简洁, 最流行, 推荐

  安装: pip install pytest
  运行: pytest

【pytest 的核心约定 (约定 > 配置)】

  1. 测试文件必须以 test_ 开头: test_models.py
  2. 测试函数必须以 test_ 开头: def test_add_student():
  3. 断言用 assert, 不用 assertEqual/setUp 等啰嗦方法

【三个核心概念】

  assert:    断言 — "我断言这个结果等于那个值"
  fixture:   夹具 — 测试前的准备和测试后的清理 (相当于 with 语句)
  parametrize: 参数化 — 同一测试跑多组数据
"""

# ============================================================
# 1. 最简单的测试 —— assert
# ============================================================
# 创建一个单独的文件 test_math.py:
#   def test_add():
#       assert 1 + 1 == 2
#   def test_multiply():
#       assert 2 * 3 == 6
#
# 运行: pytest test_math.py -v
# 输出: 2 passed ✓

# ============================================================
# 2. 给成绩系统写测试
# ============================================================

from models import Student, GradeManager


# --- 测试 Student ---

def test_student_create():
    """测试创建学生"""
    s = Student("张三", [85, 90])
    assert s.name == "张三"
    assert s.scores == [85, 90]
    assert s.average == 87.5           # (85+90)/2
    assert s.total == 175              # 85+90


def test_student_add_score():
    """测试添加成绩"""
    s = Student("张三")
    s.add_score(85)
    s.add_score(90)
    assert len(s.scores) == 2
    assert s.average == 87.5


def test_student_add_bad_score():
    """测试添加非法成绩: 应该抛 TypeError"""
    import pytest
    s = Student("张三")
    with pytest.raises(TypeError):      # 断言: 下面这行必抛 TypeError
        s.add_score("不是数字")


def test_student_eq():
    """测试相等比较: 同名 = 同一个人"""
    s1 = Student("张三", [85, 90])
    s2 = Student("张三", [50, 60])     # 同名不同分
    s3 = Student("李四", [85, 90])     # 不同名同分
    assert s1 == s2                     # 同名 → True
    assert s1 != s3                     # 不同名 → False


def test_student_lt():
    """测试排序比较: 按平均分"""
    s1 = Student("高分", [90, 95])      # 平均 92.5
    s2 = Student("低分", [60, 65])      # 平均 62.5
    assert s2 < s1                      # 低分 "小于" 高分
    assert s1 > s2                      # 有 __lt__ 就能自动推导 __gt__


def test_student_str():
    """测试字符串表示: print(student) 的输出"""
    s = Student("张三", [85, 90])
    output = str(s)
    assert "张三" in output
    assert "85" in output
    assert "87.5" in output            # 平均分


# --- 测试 GradeManager ---

def test_manager_add_and_get():
    """测试添加和获取学生"""
    m = GradeManager()
    s = Student("张三", [85, 90])
    m.add(s)
    assert len(m) == 1                  # __len__
    assert m[0] is s                    # __getitem__


def test_manager_contains():
    """测试包含检查"""
    m = GradeManager()
    s = Student("张三", [85, 90])
    m.add(s)
    # __contains__ 判断的是 Student 对象, 不是名字
    assert s in m


def test_manager_add_duplicate():
    """测试添加重复学生: 应该抛 ValueError"""
    import pytest
    m = GradeManager()
    m.add(Student("张三", [85, 90]))
    with pytest.raises(ValueError):
        m.add(Student("张三", [50, 60]))   # 同名!


def test_manager_remove():
    """测试删除学生"""
    m = GradeManager()
    m.add(Student("张三", [85, 90]))
    m.remove("张三")
    assert len(m) == 0


def test_manager_remove_not_found():
    """测试删除不存在的人: 应该抛 KeyError"""
    import pytest
    m = GradeManager()
    with pytest.raises(KeyError):
        m.remove("不存在的人")


def test_manager_filter():
    """测试筛选及格/不及格"""
    m = GradeManager()
    m.add(Student("及格生", [80, 90]))      # 平均 85
    m.add(Student("不及格生", [50, 60]))    # 平均 55

    passed = m.filter_passed()              # 列表推导式 → list
    assert len(passed) == 1
    assert passed[0].name == "及格生"

    failed = list(m.filter_failed())        # 生成器 → list
    assert len(failed) == 1
    assert failed[0].name == "不及格生"


def test_manager_rank():
    """测试排名"""
    m = GradeManager()
    m.add(Student("中", [70, 80]))          # 75
    m.add(Student("高", [90, 95]))          # 92.5
    m.add(Student("低", [50, 60]))          # 55

    ranked = m.rank(reverse=True)            # 从高到低
    assert ranked[0].name == "高"            # 第一名
    assert ranked[1].name == "中"            # 第二名
    assert ranked[2].name == "低"            # 第三名


# ============================================================
# 3. fixture —— 测试的准备和清理
# ============================================================
import pytest

@pytest.fixture
def sample_manager():
    """一个预置了 3 个学生的班级, 每个测试都能用"""
    m = GradeManager("测试班")
    m.add(Student("张三", [85, 90]))
    m.add(Student("李四", [92, 88]))
    m.add(Student("王五", [60, 55]))
    return m

def test_fixture_len(sample_manager):
    """fixture 自动作为参数传入"""
    assert len(sample_manager) == 3

def test_fixture_average(sample_manager):
    """不同的测试函数, 各自拿到全新的 fixture"""
    # 这个测试改 sample_manager 不影响上个测试
    assert sample_manager.class_average > 0


# ============================================================
# 4. parametrize —— 同一测试跑多组数据
# ============================================================

@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, -50, 50),
])
def test_parametrize_example(a, b, expected):
    """这个测试会跑 4 次, 每次用一组数据"""
    assert a + b == expected


@pytest.mark.parametrize("scores, expected_avg", [
    ([85, 90, 78], 84.3),
    ([100, 0], 50.0),
    ([], 0),                    # 空成绩 → 平均 0
    ([60], 60.0),
])
def test_average_parametrize(scores, expected_avg):
    """测试不同成绩下的平均分计算"""
    s = Student("测试", scores)
    assert abs(s.average - expected_avg) < 0.1   # 浮点数用近似比较


# ============================================================
# 5. 常用 pytest 选项
# ============================================================

# 运行方式 (在终端):
#   pytest                    # 运行所有测试
#   pytest -v                 # 详细模式, 显示每个测试的名字
#   pytest -v -s               # -s: 不捕获 print (调试时用)
#   pytest test_models.py     # 只运行指定文件
#   pytest test_models.py -k "student"  # 只运行名字含 "student" 的测试
#   pytest -x                  # 遇到第一个失败就停
#   pytest --lf                # 只跑上次失败了的测试
#   pytest --cov=models        # 查看 models.py 的测试覆盖率 (需 pip install pytest-cov)

# ============================================================
# 总结
# ============================================================
# - pytest 用约定: test_ 前缀的文件和函数
# - assert 做断言, 比 unittest 简洁
# - pytest.raises(Exception) 断言会抛异常
# - fixture 做测试准备 (像 with 语句)
# - @pytest.mark.parametrize 让一个测试跑多组数据
# - 测试文件的放法: 和代码放一起, 或在 tests/ 目录下
"""
推荐目录结构:
  grade_system/
  ├── models.py
  ├── main.py
  ├── storage.py
  └── tests/
      ├── __init__.py       # 空文件, 让 tests/ 成为一个包
      └── test_models.py    # 测试 models.py
"""
