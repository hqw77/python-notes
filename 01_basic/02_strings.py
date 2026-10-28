'''
字符串操作 -- Python 中最常用的数据类型之一

[字符串的本质]

  字符串是"字符的序列", 底层是不可变的 Unicode 字符数组.
  Python 没有"字符"类型, 单个字母也是长度为 1 的字符串.

  不可变 (immutable): 一旦创建, 不能原地修改.
    s = "hello"
    s[0] = "H"         # TypeError! 不能修改
    s = "H" + s[1:]    # 只能创建新字符串

[三种创建方式]

  '...'   : 单引号, 最简单
  "..."   : 双引号, 和单引号一样 (方便在字符串内嵌单引号)
  """...""": 三引号, 可以跨多行, 也常用于 docstring

[索引和切片 -- 字符串操作的基本功]

  s = "Python"
  s[0]     → "P"     (第一个字符)
  s[-1]    → "n"     (最后一个字符)
  s[0:3]   → "Pyt"   (索引 0,1,2, 不含 3)
  s[2:]    → "thon"  (从索引 2 到末尾)
  s[::-1]  → "nohtyP" (反转字符串! 最 Pythonic 的写法)

  切片语法: s[start:end:step]
  - start 省略 → 从头开始
  - end 省略 → 到末尾
  - step 省略 → 默认 1
  - step 为负数 → 从右往左

[编码: Python 字符串的底层]

  Python 3 的字符串是 Unicode, 内存中以码位 (code point) 存储.
  读写文件/网络传输时需要编解码:
    str.encode("utf-8")  → bytes  (字符串 → 字节, 用于输出)
    bytes.decode("utf-8") → str   (字节 → 字符串, 用于输入)

[运行方式]
  全部: python 02_strings.py
  单个: python 02_strings.py create / slice / immutable / methods / split_join / format / iterate / encoding
'''


# ============================================================
# 案例 1: 创建方式与转义
# ============================================================
def demo_create():
    print("--- 创建方式 ---")
    s1 = '单引号'
    s2 = "双引号, 里面可以有'single quotes'"
    s3 = """三引号可以
跨多行"""
    print(f"  s1: {s1}")
    print(f"  s2: {s2}")
    print(f"  s3: {s3}")

    print("\n--- 转义字符 ---")
    print(f"  \\n 换行\n  \\t 制表\t符")
    print(f"  \\\\ 反斜杠: \\")
    print(f"  \\\" 双引号: \"")

    # raw 字符串: 反斜杠就是反斜杠, 不转义 (正则表达式和 Windows 路径常用)
    path = r"C:\Users\test"
    print(f"  实际 raw 路径: {path}")


# ============================================================
# 案例 2: 索引与切片
# ============================================================
def demo_slice():
    s = "Python"
    print("--- 索引与切片 ---")
    print(f"  原字符串: {s!r}")
    print(f"  s[0] = {s[0]!r}")          # P
    print(f"  s[-1] = {s[-1]!r}")        # n
    print(f"  s[0:3] = {s[0:3]!r}")      # Pyt
    print(f"  s[2:] = {s[2:]!r}")        # thon
    print(f"  s[:3] = {s[:3]!r}")        # Pyt
    print(f"  s[::-1] = {s[::-1]!r}")    # nohtyP -- 反转字符串
    print(f"  s[::2] = {s[::2]!r}")      # Pto -- 隔一个取一个
    print(f"  s[-3:] = {s[-3:]!r}")      # hon -- 最后三个字符


# ============================================================
# 案例 3: 不可变性
# ============================================================
def demo_immutable():
    s = "Python"
    print("--- 不可变性 ---")
    try:
        s[0] = "X"
    except TypeError as e:
        print(f"  s[0] = 'X' → TypeError: {e}")

    # 正确做法: 创建新字符串
    new_s = "J" + s[1:]
    print(f"  创建新字符串: {new_s}")    # Jython


# ============================================================
# 案例 4: 常用方法
# ============================================================
def demo_methods():
    print("--- 大小写 ---")
    print(f"  'Hello'.upper() = {'Hello'.upper()!r}")
    print(f"  'Hello'.lower() = {'Hello'.lower()!r}")
    print(f"  'hello world'.title() = {'hello world'.title()!r}")

    print("\n--- 去除空白 ---")
    print(f"  '  hi  '.strip() = {'  hi  '.strip()!r}")
    print(f"  '  hi  '.lstrip() = {'  hi  '.lstrip()!r}")
    print(f"  '  hi  '.rstrip() = {'  hi  '.rstrip()!r}")

    print("\n--- 查找与替换 ---")
    print(f"  'hello'.find('l') = {'hello'.find('l')}")       # 2 (第一个 l 的索引)
    print(f"  'hello'.find('x') = {'hello'.find('x')}")       # -1 (找不到)
    print(f"  'hello'.index('l') = {'hello'.index('l')}")     # 2 (和 find 一样, 但找不到会抛 ValueError)
    print(f"  'hello'.startswith('he') = {'hello'.startswith('he')}")
    print(f"  'hello'.endswith('lo') = {'hello'.endswith('lo')}")
    print(f"  'hello'.replace('l', 'L') = {'hello'.replace('l', 'L')!r}")

    print("\n--- 判断类方法 ---")
    print(f"  '123'.isdigit() = {'123'.isdigit()}")
    print(f"  'abc'.isalpha() = {'abc'.isalpha()}")
    print(f"  'abc123'.isalnum() = {'abc123'.isalnum()}")
    print(f"  '  '.isspace() = {'  '.isspace()}")


# ============================================================
# 案例 5: split() 与 join() -- 互为逆操作
# ============================================================
def demo_split_join():
    print("--- split(): 字符串 → 列表 ---")
    csv_line = "apple,banana,orange"
    print(f"  '{csv_line}'.split(',') = {csv_line.split(',')}")
    print(f"  'a b  c'.split() = {'a b  c'.split()!r}")        # 默认按空白分割
    print(f"  'a,b,c'.split(',', 1) = {'a,b,c'.split(',', 1)}")  # 只分 1 次

    print("\n--- join(): 列表 → 字符串 ---")
    fruits = ['apple', 'banana', 'orange']
    print(f"  ','.join({fruits}) = {','.join(fruits)!r}")
    print(f"  ' -> '.join({fruits}) = {' -> '.join(fruits)!r}")

    # join 比 + 拼接高效得多:
    # "a" + "b" + "c" → 创建 2 个中间字符串对象
    # "".join(["a", "b", "c"]) → 先算总长度, 一次分配内存


# ============================================================
# 案例 6: 字符串格式化
# ============================================================
def demo_format():
    name, age = "Alice", 25

    print("--- 字符串格式化 ---")
    # f-string (Python 3.6+, 推荐)
    print(f"  f-string: 我叫{name}, 今年{age}岁")
    print(f"  f-string 表达式: {age} 年后 {age + 5}")
    print(f"  f-string 格式化: {3.14159:.2f}")   # 保留 2 位小数

    # .format() (Python 2.6+, 兼容)
    print("  .format: 我叫{}, 今年{}岁".format(name, age))
    print("  .format 命名: 我叫{n}, 今年{a}岁".format(n=name, a=age))

    # % 格式化 (旧式, 不推荐新代码使用)
    print("  %% 格式化: 我叫%s, 今年%d岁" % (name, age))


# ============================================================
# 案例 7: 遍历与计数
# ============================================================
def demo_iterate():
    print("--- 遍历字符串 ---")
    for i, ch in enumerate("ABC"):
        print(f"    s[{i}] = {ch!r}")

    print(f"\n  'hello'.count('l') = {'hello'.count('l')}")   # 2


# ============================================================
# 案例 8: 编码
# ============================================================
def demo_encoding():
    print("--- 编码 ---")
    chinese = "你好"
    print(f"  ord('A') = {ord('A')}")           # 65 (Unicode 码位)
    print(f"  chr(65) = {chr(65)!r}")           # 'A'
    utf8_bytes = chinese.encode("utf-8")
    print(f"  '你好'.encode('utf-8') = {utf8_bytes}")
    print(f"  decode 回来 = {utf8_bytes.decode('utf-8')}")


# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "create": demo_create,
        "slice": demo_slice,
        "immutable": demo_immutable,
        "methods": demo_methods,
        "split_join": demo_split_join,
        "format": demo_format,
        "iterate": demo_iterate,
        "encoding": demo_encoding,
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
# - 字符串不可变, 所有"修改"都是创建新字符串
# - 切片 s[start:end:step], s[::-1] 反转字符串
# - split() 拆开, join() 合并, 互为逆操作
# - f-string 是最推荐的格式化方式
# - find() 返回索引, 找不到返回 -1; index() 找不到抛异常
# - encode()/decode() 做字节和字符串的转换
