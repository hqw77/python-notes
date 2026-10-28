"""
pathlib 模块 —— 面向对象的路径操作

【问题场景: os.path 的字符串拼来拼去，又长又容易错】

  旧写法（字符串拼接，函数层层嵌套）：
      import os, os.path
      base = os.path.dirname(os.path.abspath(__file__))
      path = os.path.join(base, "data", "user.json")
      if os.path.exists(path) and os.path.isfile(path):
          stem = os.path.splitext(os.path.basename(path))[0]
          with open(path, encoding="utf-8") as f:
              text = f.read()

  新写法（路径是对象，属性直接取）：
      from pathlib import Path
      path = Path(__file__).parent / "data" / "user.json"
      if path.is_file():
          stem = path.stem
          text = path.read_text(encoding="utf-8")

  这也是为什么新代码几乎都用 pathlib：可读性差距是数量级的。

【核心概念】

  ┌────────────────────────────┬──────────────────────────────────────┐
  │ Path("a") / "b" / "c.txt"  │ 用 / 拼接（比 os.path.join 短）      │
  │ .name .stem .suffix        │ 文件名 / 去掉后缀的名字 / 后缀       │
  │ .parent .parents .parts    │ 上级 / 所有上级 / 拆成元组           │
  │ .exists() .is_file() ...   │ 判断类型                             │
  │ .glob("*.py") .rglob()     │ 按模式找 / 递归找                    │
  │ .read_text() .write_text() │ 一行读写文本                         │
  │ .mkdir(parents=True)       │ 建目录，自动创建中间层               │
  └────────────────────────────┴──────────────────────────────────────┘

  注意：Path 只处理路径，不负责"文件内容格式"；读出来还是字符串/字节。

【运行方式】
  全部: python 03_pathlib.py
  单个: python 03_pathlib.py create / parts / query / read_write / manipulate / compare / use_cases
"""

import os
import tempfile
from collections import defaultdict
from pathlib import Path


# ============================================================
# 1. 创建路径与拼接
# ============================================================
def demo_create():
    print("--- 1. 创建路径与拼接 ---")

    p = Path("data") / "reports" / "2024" / "summary.csv"
    print(f"  Path('data') / 'reports' / ... -> {p}")
    print(f"  字符串化: {str(p)}")
    print(f"  也能从字符串直接造: {Path('a/b/c.txt')}")

    print(f"  当前目录: {Path.cwd()}")
    print(f"  用户主目录: {Path.home()}")
    print(f"  脚本所在目录: {Path(__file__).parent}")

    # 混合类型也可以
    print(f"  和字符串混用: {Path('logs') / ('run' + str(1)) / 'app.log'}")


# ============================================================
# 2. 拆路径：name / stem / suffix / parent / parts
# ============================================================
def demo_parts():
    print("--- 2. 拆路径 ---")

    p = Path("archive") / "backup.tar.gz"
    print(f"  路径: {p}")
    print(f"  .name   文件名:   {p.name}")
    print(f"  .stem   去后缀:   {p.stem}        <- 只去掉最后一个后缀")
    print(f"  .suffix 后缀:     {p.suffix}")
    print(f"  .suffixes 所有后缀: {p.suffixes}")
    print(f"  .parent 上级:     {p.parent}")
    print(f"  .parents 所有上级: {[str(x) for x in p.parents]}")
    print(f"  .parts  拆成元组: {p.parts}")

    # 换名字 / 换后缀
    print(f"  with_suffix('.zip'): {p.with_suffix('.zip')}")
    print(f"  with_name('a.txt'):  {p.with_name('a.txt')}")
    print(f"  with_stem('x'):      {p.with_stem('x')}   (3.9+)")


# ============================================================
# 3. 查询：存在性、类型、遍历
# ============================================================
def demo_query():
    print("--- 3. 查询与遍历目录 ---")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a.txt").write_text("x", encoding="utf-8")
        (root / "b.py").write_text("print(1)", encoding="utf-8")
        sub = root / "sub"
        sub.mkdir()
        (sub / "c.py").write_text("print(2)", encoding="utf-8")

        print(f"  a.txt 存在: {(root / 'a.txt').exists()}")
        print(f"  a.txt 是文件: {(root / 'a.txt').is_file()}")
        print(f"  sub 是目录: {sub.is_dir()}")
        print(f"  不存在的路径: {(root / 'nope.txt').exists()}")

        print(f"  iterdir(): {sorted(x.name for x in root.iterdir())}")
        print(f"  glob('*.txt'): {sorted(x.name for x in root.glob('*.txt'))}")
        print(f"  rglob('*.py'): {sorted(x.name for x in root.rglob('*.py'))}   <- 递归")
        print(f"  glob('sub/*.py'): {[x.name for x in root.glob('sub/*.py')]}")

        f = root / "a.txt"
        st = f.stat()
        print(f"  stat().st_size = {st.st_size} 字节")


# ============================================================
# 4. 读写文件
# ============================================================
def demo_read_write():
    print("--- 4. 一行读写文本 ---")

    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "note.txt"

        f.write_text("第一行\n第二行\n", encoding="utf-8")
        print(f"  write_text 后大小: {f.stat().st_size} 字节")

        text = f.read_text(encoding="utf-8")
        print(f"  read_text: {text!r}")

        # 追加（write_text 会覆盖，追加要用 open）
        with f.open("a", encoding="utf-8") as fh:
            fh.write("第三行\n")
        print(f"  追加后行数: {len(f.read_text(encoding='utf-8').splitlines())}")

        # 按行读
        lines = [line.strip() for line in f.read_text(encoding="utf-8").splitlines()]
        print(f"  拆成行: {lines}")

        # 二进制
        b = Path(tmp) / "blob.bin"
        b.write_bytes(b"\x00\x01\x02")
        print(f"  write_bytes / read_bytes: {b.read_bytes()!r}")

    print("  提示: 一定要写 encoding='utf-8'，Windows 默认编码是 gbk")


# ============================================================
# 5. 增删改：目录与文件
# ============================================================
def demo_manipulate():
    print("--- 5. 建目录、改名、删除 ---")

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "a" / "b" / "c"
        base.mkdir(parents=True, exist_ok=True)   # 自动创建中间层，已存在不报错
        print(f"  建出多层目录: {base.relative_to(tmp)}")

        f = base / "x.txt"
        f.write_text("hi", encoding="utf-8")

        renamed = f.rename(base / "y.txt")        # rename 返回新路径
        print(f"  rename 后旧路径存在: {f.exists()}, 新路径存在: {renamed.exists()}")

        renamed.replace(base / "z.txt")
        print(f"  replace 改名: {sorted(p.name for p in base.iterdir())}")

        (base / "z.txt").unlink()                 # 删文件
        base.rmdir()                              # 删空目录
        print(f"  删除后 {base.name} 还在吗: {base.exists()}")

        print(f"  relative_to 求相对路径: {Path('/a/b/c.txt').relative_to('/a')}")
        try:
            Path("/a/c.txt").relative_to("/a/b")
        except ValueError as e:
            print(f"  不在同一分支时会报错: {type(e).__name__}")


# ============================================================
# 6. pathlib vs os.path
# ============================================================
def demo_compare():
    print("--- 6. pathlib vs os.path 对照 ---")

    rows = [
        ("拼路径", "os.path.join(a, b, 'c.txt')", "Path(a) / b / 'c.txt'"),
        ("取文件名", "os.path.basename(p)", "Path(p).name"),
        ("去后缀", "os.path.splitext(p)[0]", "Path(p).stem"),
        ("取后缀", "os.path.splitext(p)[1]", "Path(p).suffix"),
        ("取目录", "os.path.dirname(p)", "Path(p).parent"),
        ("判断存在", "os.path.exists(p)", "Path(p).exists()"),
        ("判断文件", "os.path.isfile(p)", "Path(p).is_file()"),
        ("绝对路径", "os.path.abspath(p)", "Path(p).resolve()"),
        ("建目录", "os.makedirs(p, exist_ok=True)", "Path(p).mkdir(parents=True, exist_ok=True)"),
        ("列目录", "os.listdir(p)", "list(Path(p).iterdir())"),
        ("读文本", "open(p).read()", "Path(p).read_text()"),
    ]
    print(f"  {'操作':<8}{'os.path':<42}{'pathlib'}")
    for op, old, new in rows:
        print(f"  {op:<8}{old:<42}{new}")

    print("  os.path 依然在用的场景: 需要把路径当纯字符串处理、或兼容很老的代码")


# ============================================================
# 7. 实战：扫描目录，统计扩展名与最大的文件
# ============================================================
def demo_use_cases():
    print("--- 7. 实战: 扫描目录 ---")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "src").mkdir()
        (root / "src" / "main.py").write_text("x" * 400, encoding="utf-8")
        (root / "src" / "util.py").write_text("y" * 120, encoding="utf-8")
        (root / "README.md").write_text("z" * 900, encoding="utf-8")
        (root / "data.json").write_text("{}", encoding="utf-8")

        files = [p for p in root.rglob("*") if p.is_file()]
        print(f"  共 {len(files)} 个文件")

        # 按扩展名分组
        by_suffix = defaultdict(list)
        for p in files:
            by_suffix[p.suffix or "(无后缀)"].append(p.name)
        print(f"  按扩展名: {dict(by_suffix)}")

        # 最大的 3 个
        largest = sorted(files, key=lambda p: p.stat().st_size, reverse=True)[:3]
        for p in largest:
            print(f"  {p.relative_to(root)!s:<20} {p.stat().st_size:>5} 字节")

        # 总大小（人类可读）
        total = sum(p.stat().st_size for p in files)
        print(f"  目录总大小: {total / 1024:.1f} KB")

    print("  这就是 find + du 的 Python 版，写脚本时非常常用")


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "create": demo_create,
        "parts": demo_parts,
        "query": demo_query,
        "read_write": demo_read_write,
        "manipulate": demo_manipulate,
        "compare": demo_compare,
        "use_cases": demo_use_cases,
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
# 常用操作速记:
#   拼路径      Path(a) / b / "c.txt"
#   拆路径      .name / .stem / .suffix(es) / .parent(s) / .parts
#   判断        .exists() / .is_file() / .is_dir()
#   遍历        .iterdir() / .glob("*.py") / .rglob("*.py")
#   读写        .read_text(encoding="utf-8") / .write_text(s)
#   建删        .mkdir(parents=True, exist_ok=True) / .unlink() / .rmdir()
#   改名        .rename()（返回新路径） / .replace()
#   绝对化      .resolve()
#
# 三个坑:
#   1. 读写文本一定要显式 encoding="utf-8"，Windows 默认是 gbk
#   2. rmdir() 只能删空目录，要递归删用 shutil.rmtree()
#   3. glob 匹配的是路径模式不是正则，"**" 递归、"[abc]" 字符集
