# 工程化笔记 —— 从写代码到写项目

## 目录

1. [虚拟环境与包管理](#1-虚拟环境与包管理)
2. [单元测试 (pytest)](#2-单元测试-pytest)
3. [类型注解](#3-类型注解)

---

## 1. 虚拟环境与包管理

### 为什么需要?

不同项目可能需要同一个包的不同版本。全局安装会冲突。

```
项目A: Django 3.2
项目B: Django 5.0

全装一起 → 打架 → 必有一个跑不了
```

虚拟环境 = 给每个项目一个独立的 Python 包仓库, 互不干扰。

### 创建和使用

```bash
# 在项目目录下创建 .venv
python -m venv .venv

# 激活 (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# 激活 (macOS/Linux)
source .venv/bin/activate

# 退出
deactivate
```

### pip 常用命令

| 命令 | 作用 |
|---|---|
| `pip install requests` | 安装包 |
| `pip install requests==2.28.0` | 安装指定版本 |
| `pip uninstall requests` | 卸载 |
| `pip list` | 查看已安装 |
| `pip freeze > requirements.txt` | 导出依赖清单 |
| `pip install -r requirements.txt` | 从清单安装 |

### 版本号写法

| 写法 | 含义 |
|---|---|
| `==2.28.0` | 精确等于 |
| `>=2.28.0` | 大于等于 |
| `~=2.28.0` | 兼容版本: >=2.28.0 且 <2.29.0 |

### 换国内镜像

```bash
# 临时
pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple

# 永久
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 2. 单元测试 (pytest)

### 为什么测试?

- 没测试: 改一行代码 → 不知道炸了哪里 → 上线崩 → 加班
- 有测试: 改一行代码 → 跑测试 → 红了马上知道 → 下班

### 核心约定

| 约定 | 说明 |
|---|---|
| 测试文件以 `test_` 开头 | `test_models.py` |
| 测试函数以 `test_` 开头 | `def test_add_student():` |
| 断言用 `assert` | 简洁, 不需要 `assertEqual` 等 |

### 三个核心概念

**assert —— 断言**

```python
def test_create():
    s = Student("张三", [85, 90])
    assert s.name == "张三"        # 断言通过
    assert s.average == 87.5       # 断言通过
```

**异常断言**

```python
import pytest

def test_error():
    with pytest.raises(TypeError):  # 断言下面必抛 TypeError
        s.add_score("不是数字")
```

**fixture —— 测试的准备和清理**

```python
@pytest.fixture
def manager():
    """每个用到这个 fixture 的测试, 都会拿到一个全新的 manager"""
    m = GradeManager()
    m.add(Student("张三", [85, 90]))
    return m

def test_len(manager):        # fixture 作为参数自动传入
    assert len(manager) == 1
```

**parametrize —— 一组数据跑同一个测试**

```python
@pytest.mark.parametrize("scores, expected", [
    ([85, 90, 78], 84.3),
    ([100, 0], 50.0),
    ([], 0),
])
def test_average(scores, expected):
    s = Student("测试", scores)
    assert abs(s.average - expected) < 0.1
```

### 常用命令

| 命令 | 作用 |
|---|---|
| `pytest tests/ -v` | 运行所有测试, 详细模式 |
| `pytest tests/ -v -k "student"` | 只跑名字含 student 的测试 |
| `pytest tests/ -x` | 遇到第一个失败就停 |
| `pytest tests/ --lf` | 只跑上次失败的测试 |
| `pytest tests/ --cov=.` | 查看覆盖率 (需 pip install pytest-cov) |

### 推荐目录结构

```
project/
├── models.py
├── main.py
└── tests/
    ├── __init__.py      # 空文件
    └── test_models.py
```

---

## 3. 类型注解

### 是什么?

在代码里标注变量和参数的类型。运行时完全忽略, 但 IDE 和静态检查器会利用它们。

```python
def average(scores: list[int]) -> float:   # 参数是 int 列表, 返回 float
    return sum(scores) / len(scores)
```

### 为什么用?

1. IDE 自动补全更准
2. 静态检查器 (mypy/pyright) 提前发现类型错误
3. 当成文档看: 看到签名就知道该传什么

### 常用类型速查

| 写法 | 含义 |
|---|---|
| `int`, `str`, `float`, `bool` | 基本类型 |
| `None` | 空值 |
| `list[int]` | int 列表 |
| `dict[str, int]` | key 是 str, value 是 int 的字典 |
| `tuple[str, float]` | str + float 二元组 |
| `set[str]` | str 集合 |
| `X \| Y` | X 或 Y (Union, Python 3.10+) |
| `X \| None` | X 或 None (Optional, Python 3.10+) |
| `Any` | 任意类型 |
| `Callable[[int], str]` | 接收 int 返回 str 的函数 |
| `TypeVar("T")` | 泛型: 保持类型信息 |
| `TypedDict` | 有类型约束的字典结构 |
| `Literal["A", "B"]` | 限定为特定字面值 |
| `Final` | 常量标记 |

### 静态检查

```bash
pip install mypy
mypy models.py    # 检查 models.py 的类型
```

VS Code 的 Pylance/Pyright 已内置实时检查, 不装 mypy 也能看到红色波浪线。

### 给成绩系统加类型注解

```python
class Student:
    def __init__(self, name: str, scores: list[int] | None = None) -> None:
        self.name: str = name
        self._scores: list[int] = list(scores) if scores else []

    @property
    def average(self) -> float:
        if not self._scores:
            return 0.0
        return sum(self._scores) / len(self._scores)


class GradeManager:
    def __getitem__(self, index: int) -> Student:
        return self._students[index]

    def find(self, name: str) -> Student | None:
        for s in self._students:
            if s.name == name:
                return s
        return None
```

---

## 速查: 工程化工具链

| 阶段 | 工具 | 一句话 |
|---|---|---|
| 环境隔离 | `venv` | 给每个项目独立空间 |
| 包管理 | `pip` | 安装/卸载/导出依赖 |
| 测试 | `pytest` | 跑测试, 看有没有写炸 |
| 类型检查 | `mypy` / `pyright` | 没运行就发现类型错误 |
| 代码格式化 | `ruff` / `black` | 自动统一代码风格 (可选) |
| 依赖管理增强 | `uv` | pip 的 10-100 倍速替代 (可选) |

---

## 学习路径

```
01_venv.md       → 看懂虚拟环境, 会用 pip
02_pytest.py     → 会给自己的代码写测试, 会跑 pytest
03_type_hints.py → 会加类型注解, 让 IDE 帮你找错
```
