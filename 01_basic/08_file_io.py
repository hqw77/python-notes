"""
文件读写 —— 数据持久化的基础

【核心原则: 用 with 语句】

  with open("file.txt", "r") as f:
      content = f.read()
  # 离开 with 块, 文件自动关闭, 即使发生异常也会关闭

  永远用 with, 不要手动 f.close().
  这是上下文管理器的核心应用 (详见 03_advanced/12_context_manager.py).

【文件模式速查】

  ┌──────┬────────────────────────────────────────────────────┐
  │ 模式  │ 含义                                                │
  ├──────┼────────────────────────────────────────────────────┤
  │ 'r'  │ 读取 (默认), 文件必须存在                              │
  │ 'w'  │ 写入, 覆盖已有内容, 文件不存在则创建                     │
  │ 'a'  │ 追加, 在文件末尾添加, 文件不存在则创建                    │
  │ 'x'  │ 创建新文件, 文件已存在则报错                            │
  │ 'b'  │ 二进制模式 (与上面组合: 'rb', 'wb')                     │
  │ '+'  │ 读写模式 (与上面组合: 'r+', 'w+')                       │
  └──────┴────────────────────────────────────────────────────┘

【encoding 参数 —— 一定要指定!】

  open("file.txt", "r", encoding="utf-8")
  不指定 encoding 的话, Windows 默认用 GBK, Linux/Mac 用 UTF-8,
  会导致跨平台时乱码问题.

【读取方式的选择】

  f.read():       一次性读入整个文件 → 小文件
  f.readline():   读一行 → 需要逐行处理
  f.readlines():  读所有行, 返回 list → 小心大文件内存爆炸
  for line in f:  逐行迭代 → 大文件最佳实践 (内存友好)

【运行方式】
  全部: python 08_file_io.py
  单个: python 08_file_io.py write / read / append / json / tools / cleanup
"""

import os
import json
from pathlib import Path

# ============================================================
# 1. 写文件
# ============================================================
def demo_write():
    print("--- 写文件 ---")

    with open("test_data.txt", "w", encoding="utf-8") as f:
        f.write("Hello, Python!\n")
        f.write("第二行\n")
        f.writelines(["第三行\n", "第四行\n"])

    print("  已写入 test_data.txt")

# ============================================================
# 2. 读文件
# ============================================================
def demo_read():
    print("\n--- 读文件 ---")

    # 先写入文件, 保证 demo 自包含 (不依赖 demo_write)
    with open("test_data.txt", "w", encoding="utf-8") as f:
        f.write("Hello, Python!\n")
        f.write("第二行\n")
        f.writelines(["第三行\n", "第四行\n"])

    # 一次性读入
    with open("test_data.txt", "r", encoding="utf-8") as f:
        content = f.read()
    print(f"  f.read():\n{content}")

    # 逐行迭代 (大文件推荐)
    print("  逐行迭代:")
    with open("test_data.txt", "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            print(f"    第 {line_no} 行: {line.rstrip()!r}")

# ============================================================
# 3. 追加写入 (a 模式)
# ============================================================
def demo_append():
    print("\n--- 追加写入 ---")

    # 先写入基础内容, 保证 demo 自包含 (不依赖 demo_write)
    with open("test_data.txt", "w", encoding="utf-8") as f:
        f.write("Hello, Python!\n")
        f.write("第二行\n")
        f.writelines(["第三行\n", "第四行\n"])

    with open("test_data.txt", "a", encoding="utf-8") as f:
        f.write("追加的一行\n")

    with open("test_data.txt", "r", encoding="utf-8") as f:
        print(f"  追加后内容: {f.readlines()!r}")

# ============================================================
# 4. JSON 读写
# ============================================================
def demo_json():
    print("\n--- JSON 读写 ---")

    data = {
        "name": "Alice",
        "age": 30,
        "languages": ["Python", "JavaScript"]
    }

    # Python → JSON 字符串
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    print(f"  json.dumps:\n{json_str}")

    # Python → JSON 文件
    with open("test_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # JSON 文件 → Python
    with open("test_data.json", "r", encoding="utf-8") as f:
        loaded = json.load(f)
    print(f"  读回的数据: {loaded}")
    print(f"  name = {loaded['name']}")

# ============================================================
# 5. 文件操作工具
# ============================================================
def demo_tools():
    print("\n--- 文件操作工具 ---")

    # 先写入文件, 保证 demo 自包含 (不依赖 demo_write)
    with open("test_data.txt", "w", encoding="utf-8") as f:
        f.write("Hello, Python!\n")

    # 路径操作 (os.path)
    print(f"  os.path.exists('test_data.txt'): {os.path.exists('test_data.txt')}")
    print(f"  os.path.getsize('test_data.txt'): {os.path.getsize('test_data.txt')} 字节")

    # 更现代的 pathlib (见 04_stdlib/04_pathlib.py)
    p = Path("test_data.txt")
    print(f"  用 pathlib: {p.name}, {p.absolute()}, {p.stat().st_size} 字节")

# ============================================================
# 6. 清理测试文件
# ============================================================
def demo_cleanup():
    # 用 os.path.exists 判断, 避免文件不存在时报错
    if os.path.exists("test_data.txt"):
        os.remove("test_data.txt")
    if os.path.exists("test_data.json"):
        os.remove("test_data.json")
    print("\n  已清理测试文件")

# ============================================================
# 入口: 支持跑全部 / 跑单个
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "write": demo_write,
        "read": demo_read,
        "append": demo_append,
        "json": demo_json,
        "tools": demo_tools,
        "cleanup": demo_cleanup,
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
# - 永远用 with open() 而不是手动 close
# - 始终指定 encoding="utf-8"
# - 大文件用 for line in f: 逐行读
# - 写入时注意模式: w 覆盖, a 追加, x 创建
# - json.dump/load 做 JSON 序列化
# - pathlib 比 os.path 更现代, 推荐使用
