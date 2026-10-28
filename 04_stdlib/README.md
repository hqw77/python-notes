# 标准库 `04_stdlib/`

Python 内置的常用模块，日常开发的高频工具。

## 已完成

| # | 文件 | 内容 | 案例 |
|---|---|---|---|
| 02 | [02_itertools.py](02_itertools.py) | 无限迭代器、终止型迭代器、排列组合、分组、切片、`pairwise`、`tee`、滑动窗口 | 11 个 |

## 待补（目前只有知识点大纲）

| # | 文件 | 计划覆盖 |
|---|---|---|
| 01 | 01_collections.py | namedtuple、deque、Counter、defaultdict、ChainMap、UserDict |
| 03 | 03_functools.py | reduce、partial、lru_cache、cached_property、wraps、singledispatch、total_ordering |
| 04 | 04_pathlib.py | Path 拼接、属性、遍历、读写、resolve、与 os.path 对比 |
| 05 | 05_datetime.py | date/time/datetime、timedelta、strptime/strftime、时区、ISO 格式 |
| 06 | 06_regex.py | 字符类、分组、贪婪/非贪婪、断言、search/match/findall/sub、常用正则 |
| 07 | 07_json_csv.py | dumps/loads、ensure_ascii、default、DictReader/DictWriter、BOM、大文件 |
| 08 | 08_logging.py | 级别、Logger、Handler、Formatter、轮转、父子 logger |

> `iterator.py`（迭代器协议）和 `with.py`（上下文管理器）属于语言协议，已移到
> [`03_advanced/`](../03_advanced/)（现为 `11_iterator.py`、`12_context_manager.py`）。

## 填充约定

新增案例统一采用下面的结构，和 [`06_concurrency/`](../06_concurrency/) 保持一致：

```python
def demo_xxx():
    """案例: ..."""

if __name__ == "__main__":
    import sys
    demos = {"xxx": demo_xxx, ...}
    # 传参跑单个案例，不传跑全部，传错名字列出可选
```

要求：

- 每个文件独立可运行，`python 03_functools.py` 跑全部，`python 03_functools.py cache` 跑单个
- 每个文件 200–350 行，顶部 docstring 写【问题场景】【核心概念】，文末写「总结」
- 案例里的输出是真实运行结果，不是伪代码
