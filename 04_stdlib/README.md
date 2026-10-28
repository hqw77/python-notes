# 标准库 `04_stdlib/`

只保留 5 个高频模块。`datetime`、`re` 这种"用到再查"的模块不再占位；
`itertools` 属于迭代器工具，已归入 [`03_advanced/13_itertools.py`](../03_advanced/13_itertools.py)。

## 进度

| # | 文件 | 内容 | 状态 |
|---|---|---|---|
| 01 | [01_collections.py](01_collections.py) | namedtuple、Counter、defaultdict、deque、OrderedDict、ChainMap + 日志分析实战 | ✅ 7 个案例 |
| 02 | [02_functools.py](02_functools.py) | lru_cache、cached_property、partial、wraps、singledispatch、total_ordering、cmp_to_key、reduce | ✅ 9 个案例 |
| 03 | [03_pathlib.py](03_pathlib.py) | 拼接与拆解、查询遍历、读写、增删改、与 os.path 对照、扫描目录实战 | ✅ 7 个案例 |
| 04 | [04_json_csv.py](04_json_csv.py) | JSON 序列化/反序列化、datetime 处理、CSV 读写、BOM、大文件流式、CSV→JSON 实战 | ✅ 7 个案例 |
| 05 | [05_logging.py](05_logging.py) | 级别过滤、Logger 层级、Handler + Formatter、轮转、异常堆栈、通用配置实战 | ✅ 8 个案例 |

## 为什么只留 5 个

标准库有 200 多个模块，全学不现实。筛选标准是「写代码时每周至少碰到一次」：

- `collections` / `functools` —— 写业务逻辑天天用，且能体现 Python 的设计思想
- `pathlib` / `json_csv` —— 任何读写文件、导数据的场景
- `logging` —— 任何要长期跑的东西

`datetime`（时区）、`re`（正则）不是不重要，而是更适合"用到时查文档 + 在真实项目里练"，
放在这里当空壳反而拉低整章的完成度。

## 填充约定

新增案例统一采用下面的结构，和 [`05_concurrency/`](../05_concurrency/) 保持一致：

```python
def demo_xxx():
    """案例: ..."""

if __name__ == "__main__":
    import sys
    demos = {"xxx": demo_xxx, ...}
    # 传参跑单个案例，不传跑全部，传错名字列出可选
```

要求：

- 每个文件独立可运行：`python 03_pathlib.py` 跑全部，`python 03_pathlib.py glob` 跑单个
- 每个文件 200–400 行，顶部 docstring 写【问题场景】【核心概念】，文末写「总结」
- 案例里的输出是真实运行结果，不是伪代码
