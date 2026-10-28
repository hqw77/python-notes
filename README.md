# Python 学习路线

> 记录 Python 语言本身的学习过程：基础语法 → 面向对象 → 进阶特性 → 标准库 → 工程化 → 并发编程。
> 每个知识点都落成可运行的 `.py` 案例，不是纯文字笔记。
>
> 后端方向（FastAPI、MySQL）单独成库：`Backend-notes`。

## 目录结构

```
python-notes/
├── 01_basic/              # 基础语法
├── 02_oop/                # 面向对象
├── 03_advanced/           # 进阶特性（魔术方法 / 装饰器 / 描述符 / 生成器 / 异步）
├── 04_stdlib/             # 标准库
├── 05_tooling/            # 工程化（venv / pytest / 类型注解）
├── 06_concurrency/        # 并发编程（线程 / 进程 / 协程）
│   └── docs/并发编程.md      # 11 章完整长文教程
├── E_S_Docs/              # 面试八股整理
└── README.md              # 本文件
```

## 怎么跑

每个文件都能单独执行；并发章节还支持只跑某个案例（传错名字会列出可选案例）：

```bash
python 01_basic/01_variables.py          # 跑整个文件
python 06_concurrency/03_lock.py deadlock  # 只跑「死锁」这个案例
```

测试与工具链：

```bash
pip install -r requirements.txt   # 目前只有 pytest 及其依赖
pytest                            # 运行测试
```

---

## 第一阶段：基础语法 `01_basic/`

9 个文件，每个 180–240 行，按「变量 → 字符串 → 条件 → 循环 → 容器 → 函数 → 文件 → 推导式」推进。

| # | 文件 | 内容 | 状态 |
|---|---|---|---|
| 01 | 01_variables.py | 变量、基本类型、类型转换、小整数缓存、命名规范 | ✅ |
| 02 | 02_strings.py | 字符串操作、格式化、编码 | ✅ |
| 03 | 03_condition.py | 条件判断、match/case、短路求值 | ✅ |
| 04 | 04_loop.py | for/while、break/continue、enumerate/zip | ✅ |
| 05 | 05_list_tuple.py | 列表、元组、切片、拆包 | ✅ |
| 06 | 06_dict_set.py | 字典、集合、哈希原理 | ✅ |
| 07 | 07_function.py | 参数类型、作用域、lambda、闭包 | ✅ |
| 08 | 08_file_io.py | 文件读写、CSV/JSON 基础 | ✅ |
| 09 | 09_comprehension.py | 推导式、生成器表达式 | ✅ |

---

## 第二阶段：面向对象 `02_oop/`

| # | 文件 | 内容 | 状态 |
|---|---|---|---|
| 01 | 01_class_basic.py | 类与实例、self、属性、方法 | ✅ |
| 02 | 02_inheritance.py | 继承、多态、MRO、抽象基类 | ✅ |
| 03 | 03_encapsulation.py | 封装、私有属性、@property | ✅ |
| 04 | 04_classmethod.py | @classmethod、@staticmethod、__new__ | ✅ |

配套 [README.md](02_oop/README.md) 有 320 行的知识点串联。

---

## 第三阶段：进阶特性 `03_advanced/`

十三个专题：两种协议（迭代器、上下文管理器）+ itertools 工具集 + 十个魔术方法与语法特性，每个都有完整案例。配套 [README.md](03_advanced/README.md)（487 行，接近一本速查手册）。

| # | 文件 | 内容 | 状态 |
|---|---|---|---|
| 01 | 01_str_repr.py | __str__ / __repr__ | ✅ |
| 02 | 02_container.py | __getitem__ / __setitem__ / __len__ / __contains__ | ✅ |
| 03 | 03_callable.py | __call__ | ✅ |
| 04 | 04_comparison.py | __eq__ / __lt__ 等比较协议、total_ordering | ✅ |
| 05 | 05_numeric.py | __add__ / __mul__ / __iadd__ / __radd__ | ✅ |
| 06 | 06_decorator.py | 装饰器、@wraps、带参装饰器、类装饰器 | ✅ |
| 07 | 07_descriptor.py | 描述符协议、@property 底层 | ✅ |
| 08 | 08_attribute_access.py | __getattr__ / __setattr__ / __getattribute__ | ✅ |
| 09 | 09_generator_advanced.py | yield from / send() / 协程 | ✅ |
| 10 | 10_async_basics.py | async / await / asyncio | ✅ |
| 11 | 11_iterator.py | 迭代器协议（__iter__ / __next__）、生成器、内置迭代器 | ✅ |
| 12 | 12_context_manager.py | 上下文管理器（__enter__ / __exit__）、contextlib、嵌套与异常控制 | ✅ |
| 13 | 13_itertools.py | itertools：无限 / 终止 / 组合 / 分组 / 切片 / pairwise / tee | ✅ |

---

## 第四阶段：标准库 `04_stdlib/`

只保留 5 个高频模块；`itertools` 归入第三阶段的迭代器专题，`datetime` / `re` 用到再查。

| # | 文件 | 内容 | 状态 |
|---|---|---|---|
| 01 | 01_collections.py | namedtuple、Counter、defaultdict、deque、OrderedDict、ChainMap + 日志分析实战 | ✅ 7 个案例 |
| 02 | 02_functools.py | lru_cache、cached_property、partial、wraps、singledispatch、total_ordering、cmp_to_key、reduce | ✅ 9 个案例 |
| 03 | 03_pathlib.py | 路径拼接与拆解、遍历查询、读写、增删改、与 os.path 对照 | ✅ 7 个案例 |
| 04 | 04_json_csv.py | JSON 序列化、datetime 处理、CSV 读写、BOM、大文件流式 | ✅ 7 个案例 |
| 05 | 05_logging.py | 级别、Logger 层级、Handler + Formatter、轮转、异常堆栈 | ✅ 8 个案例 |

> 迭代器协议与上下文管理器属于语言特性，已归入 [`03_advanced/`](03_advanced/)（`11_iterator.py`、`12_context_manager.py`）。

---

## 第五阶段：工程化 `05_tooling/`

| # | 文件 | 内容 | 状态 |
|---|---|---|---|
| 01 | 01_venv.md | 虚拟环境、pip、包管理 | ✅ |
| 02 | 02_pytest.py | 单元测试、fixture、parametrize、常用命令 | ✅ |
| 03 | 03_type_hints.py | 类型注解、mypy 静态检查 | ✅ |

---

## 第六阶段：并发编程 `06_concurrency/`

主线是一句话：**GIL 决定线程只能切换、不能并行，所以 CPU 密集靠进程、海量 I/O 靠协程。**

| # | 文件 | 内容 | 状态 |
|---|---|---|---|
| 01 | 01_concept.py | 并发 vs 并行、GIL、I/O 密集 vs CPU 密集 | ✅ |
| 02 | 02_threading.py | Thread 创建、daemon、join、start vs run | ✅ |
| 03 | 03_lock.py | Lock / RLock、竞态条件、死锁 | ✅ |
| 04 | 04_sync_primitives.py | Semaphore / Event / Condition / Queue | ✅ |
| 05 | 05_thread_pool.py | ThreadPoolExecutor、submit / map / as_completed | ✅ |
| 06 | 06_multiprocessing.py | Process、绕过 GIL、`__main__` 约束 | ✅ |
| 07 | 07_process_comm.py | 进程间通信 Queue / Pipe / Manager | ✅ |
| 08 | 08_process_pool.py | ProcessPoolExecutor、pickle 约束 | ✅ |
| 09 | 09_async_basics.py | 协程基础：async/await、gather、create_task | ✅ |
| 10 | 10_coroutine_deep.py | 协程进阶：as_completed、timeout、to_thread | ✅ |
| 11 | 11_how_to_choose.py | 线程 vs 进程 vs 协程 选型决策树 | ✅ |

配套资料：

- [concurrency_roadmap.md](06_concurrency/concurrency_roadmap.md)：学习顺序与选型决策树
- [docs/并发编程.md](06_concurrency/docs/并发编程.md)：11 章完整长文（约 7.4 万字），每章按「为什么 → 概念 → 案例 → 误区 → 总结」展开

---

## 面试资料 `E_S_Docs/`

| 文件 | 内容 |
|---|---|
| python八股.md | 1,099 行面试问答整理 |
| clean_md.py | 清理语雀导出的 Markdown（去 HTML 标签、压空行） |

---

## 学习建议

1. **按阶段顺序学**：01 → 02 → 03 → 04 → 05 → 06，基础不牢别跳阶段。
2. **OOP 是分水岭**：类理解透了，后面的魔术方法、描述符、ORM 才看得懂。
3. **每个文件独立可运行**：跑通、看到输出，才算学完一个。
4. **不要赶进度**：光看不写等于没学，每个阶段自己写练习。
5. **并发先懂 GIL**：线程 / 进程 / 协程的区别全靠它，先读 `01_concept.py`。
6. **长文当复习材料**：先跑代码，再回看 `docs/并发编程.md` 查漏补缺。
