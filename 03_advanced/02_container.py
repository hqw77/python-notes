"""
容器协议 (Container Protocol)

[什么是容器?]
  容器就是能"装东西"的对象. Python 内置的 list, dict, tuple, set, str 都是容器.
  它们的共同特点: 可以用 [] 访问元素, 可以用 len() 看大小, 可以用 in 检查包含关系.

[什么是容器协议?]
  容器协议是一组魔术方法, 只要你实现了它们, 你的自定义类就能像 list/dict 一样
  使用 [], len(), in 等语法. Python 不关心你是什么类型, 只关心你有没有这些方法
  --这就是"鸭子类型" (如果它走起来像鸭子, 叫起来像鸭子, 那它就是鸭子).

[协议包含的方法]

  ┌─────────────────┬──────────────────────┬────────────────────────────┐
  │ 语法             │ 魔术方法              │ 说明                        │
  ├─────────────────┼──────────────────────┼────────────────────────────┤
  │ obj[key]        │ __getitem__(self,key)│ 根据 key 获取元素            │
  │ obj[key] = val  │ __setitem__(s,k,v)   │ 设置元素                    │
  │ del obj[key]    │ __delitem__(self,key)│ 删除元素                    │
  │ len(obj)        │ __len__(self)        │ 返回容器内元素个数            │
  │ x in obj        │ __contains__(s,x)    │ 检查 x 是否在容器中           │
  │ for x in obj    │ __iter__ / __getitem__│ 迭代 (见 11_iterator.py)      │
  │ reversed(obj)   │ __reversed__         │ 反向迭代 (可选)              │
  │ iter(obj)       │ __iter__             │ 返回迭代器 (见 11_iterator.py)  │
  └─────────────────┴──────────────────────┴────────────────────────────┘

[调用链路 -- Python 内部是怎么工作的]

  当你写 obj[0] 时:
    1. Python 调用 type(obj).__getitem__(obj, 0)
    2. 如果 obj 是 dict,key 可以是任何可哈希类型
    3. 如果 obj 是 list,key 可以是 int 或 slice 对象
    4. 返回值直接给你

  当你写 len(obj) 时:
    1. Python 调用 type(obj).__len__(obj)
    2. 返回值必须 >= 0 且是整数
    3. 如果返回非整数或负数,Python 会报错
    4. CPython 对 len() 有优化: 直接读 C 结构体里的 ob_size 字段,O(1) 极快

  当你写 x in obj 时:
    1. Python 先找 __contains__
    2. 如果没找到, 退而求其次用 __iter__ 逐个比较
    3. 如果还没找到, 用 __getitem__ 从 0 开始逐个比较
    4. 这意味着你只要实现了 __getitem__,"in" 就能工作 (只是慢一点)

[可变容器 vs 不可变容器]

  可变容器(list / dict / set)-- 至少要实现以下方法:
    __getitem__     读
    __setitem__     写
    __delitem__     删
    __len__         长度

  不可变容器(tuple / str / frozenset)-- 只需要:
    __getitem__     读
    __len__         长度
     (没有 __setitem__ 和 __delitem__,因为不能修改)

  所以,obj[key] = val 能成功, 不是因为对象是 list,而是因为对象的类实现了 __setitem__.
  同样,obj[key] 报 TypeError,说明连 __getitem__ 都没实现.

[与迭代器协议的关系]

  容器协议和迭代器协议经常一起出现:

  - 容器 (Container): 有 __getitem__ 或 __iter__, 能"被遍历"
  - 迭代器 (Iterator): 有 __next__ + __iter__, 能"去遍历"容器

  容器是"一筐鸡蛋", 迭代器是"正在往里拿鸡蛋的那只手".

  for 循环的查找顺序:
    for x in obj:
        ↓
    1. 先找 obj.__iter__() → 返回迭代器 → 调用迭代器的 __next__()
    2. 没找到 __iter__ → 找 obj.__getitem__(0), obj.__getitem__(1), ...
       直到抛出 IndexError 才停止
    3. 都没找到 → TypeError: object is not iterable

  这就是为什么你只写了 __getitem__, for 循环也能工作的原因 (见 section 5).

[运行方式]
  全部: python 02_container.py
  单个: python 02_container.py readonly / readwrite / grid / team / iter_priority
"""

# ============================================================
# 1. 最简单的容器 -- 只读列表
# ============================================================
def demo_readonly():
    class ReadOnlyList:
        """一个只读的包装列表"""
        def __init__(self, items):
            self._items = list(items)

        def __getitem__(self, index):
            """obj[index] 时调用"""
            return self._items[index]

        def __len__(self):
            """len(obj) 时调用"""
            return len(self._items)

        def __contains__(self, item):
            """x in obj 时调用"""
            return item in self._items

        def __repr__(self):
            return f"ReadOnlyList({self._items})"

    rol = ReadOnlyList([1, 2, 3, 4, 5])
    print("--- 只读容器 ---")
    print(f"  取索引 0: {rol[0]}")
    print(f"  取索引 -1: {rol[-1]}")
    print(f"  取切片: {rol[1:4]}")
    print(f"  len: {len(rol)}")
    print(f"  3 in rol: {3 in rol}")
    print(f"  99 in rol: {99 in rol}")


# ============================================================
# 2. 可读写的容器 -- 支持赋值
# ============================================================
def demo_readwrite():
    class MyDict:
        """一个玩具字典, 用两个平行列表存储 key 和 value"""
        def __init__(self):
            self._keys = []
            self._values = []

        def __getitem__(self, key):
            """dict[key] 取值"""
            if key not in self._keys:
                raise KeyError(key)
            idx = self._keys.index(key)
            return self._values[idx]

        def __setitem__(self, key, value):
            """dict[key] = value 赋值"""
            if key in self._keys:
                idx = self._keys.index(key)
                self._values[idx] = value
            else:
                self._keys.append(key)
                self._values.append(value)

        def __delitem__(self, key):
            """del dict[key] 删除"""
            if key not in self._keys:
                raise KeyError(key)
            idx = self._keys.index(key)
            del self._keys[idx]
            del self._values[idx]

        def __len__(self):
            return len(self._keys)

        def __contains__(self, key):
            return key in self._keys

        def __repr__(self):
            items = ", ".join(f"{k!r}: {v!r}" for k, v in zip(self._keys, self._values))
            return f"MyDict({{{items}}})"

    md = MyDict()
    print("\n--- 可读写容器 ---")
    md["name"] = "张三"
    md["age"] = 30
    print(f"  赋值后: {md}")
    print(f"  md['name']: {md['name']}")
    print(f"  len: {len(md)}")
    print(f"  'age' in md: {'age' in md}")
    del md["age"]
    print(f"  删除 age 后: {md}")


# ============================================================
# 3. 支持切片的容器
# ============================================================
def demo_grid():
    class Grid:
        """2D 网格, 支持 grid[row, col] 访问"""
        def __init__(self, rows, cols):
            self.rows = rows
            self.cols = cols
            self._data = [[0] * cols for _ in range(rows)]

        def __getitem__(self, key):
            # key 是 (row, col) 元组 - grid[1, 2] 实际是 grid[(1, 2)]
            row, col = key
            return self._data[row][col]

        def __setitem__(self, key, value):
            row, col = key
            self._data[row][col] = value

        def __repr__(self):
            return "\n".join(" ".join(f"{v:3}" for v in row) for row in self._data)

    grid = Grid(3, 4)
    print(f"\n--- 二维网格 ---")
    grid[0, 0] = 1
    grid[0, 2] = 5
    grid[1, 1] = 9
    grid[2, 3] = 7
    print(grid)
    print(f"  grid[1, 1] = {grid[1, 1]}")


# ============================================================
# 4. 可迭代的容器 -- for 循环
# ============================================================
def demo_team():
    class Team:
        """队员集合, 支持 for 循环遍历"""
        def __init__(self, *members):
            self._members = list(members)

        def __getitem__(self, index):
            """实现 __getitem__ 后, for 循环会自动工作"""
            return self._members[index]

        def __len__(self):
            return len(self._members)

        def __repr__(self):
            return f"Team{tuple(self._members)}"

    team = Team("Alice", "Bob", "Charlie")
    print(f"\n--- for 循环遍历 ---")
    print(f"  {team}")
    print(f"  第三个成员: {team[2]}")
    print("  遍历: ", end=" ")
    for member in team:
        print(member, end=" ")
    print()

    # 注: 只实现 __getitem__ 就能支持 for 循环, 但更好的做法是实现 __iter__
    # Python 找迭代器的优先级: __iter__ > __getitem__ (从 0 开始递增索引)


# ============================================================
# 5. __iter__ vs __getitem__ 的优先级
# ============================================================
def demo_iter_priority():
    class WithBoth:
        def __getitem__(self, index):
            return f"from getitem[{index}]"

        def __iter__(self):
            yield "from iter[0]"
            yield "from iter[1]"

    class OnlyGetItem:
        def __getitem__(self, index):
            if index >= 3:
                raise IndexError        # 抛出 IndexError 让 for 停止
            return f"item[{index}]"

    print(f"\n--- __iter__ 优先级高于 __getitem__ ---")
    for x in WithBoth():
        print(f"  {x}")
    # 输出 iter 的内容, 说明 __iter__ 优先

    print("\n--- 只有 __getitem__ 时, 也能 for ---")
    for x in OnlyGetItem():
        print(f"  {x}")


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "readonly": demo_readonly,
        "readwrite": demo_readwrite,
        "grid": demo_grid,
        "team": demo_team,
        "iter_priority": demo_iter_priority,
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
# - __getitem__: obj[key], 支持切片, for 循环
# - __setitem__: obj[key] = val
# - __delitem__: del obj[key]
# - __len__:     len(obj)
# - __contains__: x in obj
# - __iter__ 优先级 > __getitem__ (for 循环时优先用迭代器)
