# Python 学习路线

## 目录结构

```
d:\python_learn\
├── 01_basic/          # 第一阶段：基础语法
├── 02_oop/            # 第二阶段：面向对象
├── 03_advanced/       # 第三阶段：进阶特性（魔术方法）
├── 04_stdlib/         # 第四阶段：标准库
├── 05_tooling/        # 第五阶段：工程化
├── 06_web/            # 第六阶段：Web 开发
├── 07_concurrency/    # 第七阶段：并发编程（线程/进程/协程/锁）
└── README.md          # 本文件
```

---

## 第一阶段：基础语法 `01_basic/`

| # | 文件 | 内容 | 状态 |
|---|---|---|---|
| 01 | 01_variables.py | 变量、基本类型、类型转换 | 📝 大纲 |
| 02 | 02_strings.py | 字符串操作、格式化、编码 | 📝 大纲 |
| 03 | 03_condition.py | 条件判断、match/case、短路求值 | 📝 大纲 |
| 04 | 04_loop.py | for/while、break/continue、enumerate/zip | 📝 大纲 |
| 05 | 05_list_tuple.py | 列表、元组、切片、拆包 | 📝 大纲 |
| 06 | 06_dict_set.py | 字典、集合、哈希原理 | 📝 大纲 |
| 07 | 07_function.py | 参数类型、作用域、lambda、闭包 | 📝 大纲 |
| 08 | 08_file_io.py | 文件读写、CSV/JSON 基础 | 📝 大纲 |
| 09 | 09_comprehension.py | 推导式、生成器表达式 | 📝 大纲 |

---

## 第二阶段：面向对象 `02_oop/`

| # | 文件 | 内容 | 状态 |
|---|---|---|---|
| 01 | 01_class_basic.py | 类与实例、self、属性、方法 | 📝 大纲 |
| 02 | 02_inheritance.py | 继承、多态、MRO、抽象基类 | 📝 大纲 |
| 03 | 03_encapsulation.py | 封装、私有属性、@property | 📝 大纲 |
| 04 | 04_classmethod.py | @classmethod、@staticmethod、__new__ | 📝 大纲 |

---

## 第三阶段：进阶特性 `03_advanced/`

已学：

| # | 文件 | 内容 | 状态 |
|---|---|---|---|
| — | iter.py | 生成器入门（yield） | ✅ |
| — | iterator.py | 迭代器协议（__iter__/__next__） | ✅ |
| — | with.py | 上下文管理器（__enter__/__exit__） | ✅ |

待学：

| # | 文件 | 内容 | 状态 |
|---|---|---|---|
| 01 | 01_str_repr.py | __str__ / __repr__ | ✅ 有案例 |
| 02 | 02_container.py | __getitem__ / __setitem__ / __len__ | ✅ 有案例 |
| 03 | 03_callable.py | __call__ | ✅ 有案例 |
| 04 | 04_comparison.py | __eq__ / __lt__ / __gt__ 等 | ✅ 有案例 |
| 05 | 05_numeric.py | __add__ / __sub__ / __mul__ 等 | ✅ 有案例 |
| 06 | 06_decorator.py | 装饰器、@wraps、带参装饰器 | ✅ 有案例 |
| 07 | 07_descriptor.py | 描述符协议、@property 底层 | ✅ 有案例 |
| 08 | 08_attribute_access.py | __getattr__ / __setattr__ | ✅ 有案例 |
| 09 | 09_generator_advanced.py | yield from / send() / 协程 | ✅ 有案例 |
| 10 | 10_async_basics.py | async / await / asyncio | ✅ 有案例 |

---

## 第四阶段：标准库 `04_stdlib/`

| # | 文件 | 内容 | 状态 |
|---|---|---|---|
| 01 | 01_collections.py | namedtuple, deque, Counter, defaultdict | 📝 大纲 |
| 02 | 02_itertools.py | 迭代工具，排列组合 | 📝 大纲 |
| 03 | 03_functools.py | reduce, partial, lru_cache, wraps | 📝 大纲 |
| 04 | 04_pathlib.py | 现代路径操作 | 📝 大纲 |
| 05 | 05_datetime.py | 日期时间处理 | 📝 大纲 |
| 06 | 06_regex.py | 正则表达式 | 📝 大纲 |
| 07 | 07_json_csv.py | JSON / CSV 序列化 | 📝 大纲 |
| 08 | 08_logging.py | 日志模块 | 📝 大纲 |

---

## 第五阶段：工程化 `05_tooling/`

| # | 文件 | 内容 | 状态 |
|---|---|---|---|
| 01 | 01_venv.md | 虚拟环境、pip、包管理 | 📝 大纲 |
| 02 | 02_pytest.py | 单元测试、pytest | 📝 大纲 |
| 03 | 03_type_hints.py | 类型注解、mypy 静态检查 | 📝 大纲 |

---

## 第七阶段：并发编程 `07_concurrency/`

| # | 文件 | 内容 | 状态 |
|---|---|---|---|
| 01 | 01_concept.py | 并发 vs 并行、GIL、I/O密集 vs CPU密集 | ✅ 有案例 |
| 02 | 02_threading.py | Thread 创建、daemon、join | ✅ 有案例 |
| 03 | 03_lock.py | Lock / RLock、竞态条件、死锁 | ✅ 有案例 |
| 04 | 04_sync_primitives.py | Semaphore / Event / Condition / Queue | ✅ 有案例 |
| 05 | 05_thread_pool.py | ThreadPoolExecutor、submit/map | ✅ 有案例 |
| 06 | 06_multiprocessing.py | Process、绕过 GIL | ✅ 有案例 |
| 07 | 07_process_comm.py | 进程间通信 Queue/Pipe/Manager | ✅ 有案例 |
| 08 | 08_process_pool.py | ProcessPoolExecutor | ✅ 有案例 |
| 09 | 09_coroutine_deep.py | 协程进阶、与线程/进程混用 | ✅ 有案例 |
| 10 | 10_how_to_choose.py | 线程 vs 进程 vs 协程 选型决策树 | ✅ 有案例 |

---

## 学习建议

1. **按阶段顺序学**：01_basic → 02_oop → 03_advanced → 04_stdlib → 05_tooling → 06_web → 07_concurrency
2. **基础不牢别跳**：阶段一不熟就不要进阶段二
3. **OOP 是分水岭**：阶段二是最重要的过渡，类理解透了后面魔术方法才学得懂
4. **每个文件独立可运行**：学完一个跑通一个，看到输出才算过
5. **不要赶进度**：每个阶段写好自己的练习案例，光看不动手等于白学
6. **并发先懂 GIL**：学并发编程前先搞清 GIL，线程/进程/协程的区别全靠它

