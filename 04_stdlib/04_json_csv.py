"""
JSON 与 CSV -- 数据的进出口

[问题场景: 数据要存下来, 传出去, 读回来]

  - 配置文件, 接口返回, 日志 → JSON (结构化, 跨语言, 可嵌套)
  - Excel 导出, 批量导入, 报表 → CSV (表格, 体积小, 能用 Excel 打开)

  两者都是标准库, 不需要装包. 难的不是 API, 是几个固定套路:
    JSON: ensure_ascii=False 保中文, indent 好看, default 处理 datetime
    CSV:  用 DictReader/DictWriter (按列名而不是下标), newline="", BOM 给 Excel

[核心概念]

  ┌───────────────┬────────────────────────────────────────────────┐
  │ json.dumps    │ Python 对象 -> JSON 字符串                     │
  │ json.loads    │ JSON 字符串 -> Python 对象                     │
  │ json.dump     │ Python 对象 -> 文件                            │
  │ json.load     │ 文件 -> Python 对象                            │
  ├───────────────┼────────────────────────────────────────────────┤
  │ csv.reader    │ 逐行读成 list (最原始)                        │
  │ csv.DictReader│ 逐行读成 dict (按表头取列, 推荐)              │
  │ csv.writer    │ 逐行写 list                                    │
  │ csv.DictWriter│ 逐行写 dict (推荐)                            │
  └───────────────┴────────────────────────────────────────────────┘

  类型映射 (JSON 没有 datetime / set / 自定义类):
      dict <-> object    list/tuple <-> array    str <-> string
      int/float <-> number    True/False <-> true/false    None <-> null

[运行方式]
  全部: python 04_json_csv.py
  单个: python 04_json_csv.py json_basic / json_types / json_file / csv_basic / csv_encoding / stream / use_cases
"""

import csv
import json
import tempfile
from datetime import datetime
from pathlib import Path


# ============================================================
# 1. JSON 基本用法
# ============================================================
def demo_json_basic():
    print("--- 1. JSON: dumps / loads ---")

    data = {
        "name": "张三",
        "age": 20,
        "tags": ["python", "sql"],
        "active": True,
        "score": None,
    }

    # ensure_ascii=True (默认): 中文会被转成 \uXXXX
    compact = json.dumps(data, ensure_ascii=False)
    print(f"  dumps(ensure_ascii=False): {compact}")

    escaped = json.dumps(data)
    print(f"  dumps(ensure_ascii=True): {escaped[:70]}...")

    pretty = json.dumps(data, ensure_ascii=False, indent=2)
    print("  美化输出:")
    for line in pretty.splitlines()[:5]:
        print(f"    {line}")
    print("    ...")

    # 反序列化
    back = json.loads(compact)
    print(f"  loads 回来 == 原对象: {back == data}")
    print(f"  拿字段: back['tags'][0] = {back['tags'][0]}")

    # sort_keys 让输出稳定 (方便 diff / 做缓存 key)
    print(f"  sort_keys 排序: {json.dumps({'b': 1, 'a': 2}, sort_keys=True)}")

    # 解析错误
    try:
        json.loads("{不是合法 JSON}")
    except json.JSONDecodeError as e:
        print(f"  非法 JSON 会抛 JSONDecodeError: {e.msg} (line {e.lineno})")


# ============================================================
# 2. JSON 处理不支持的类型的
# ============================================================
def demo_json_types():
    print("--- 2. JSON: 处理 datetime 等不支持的类 ---")

    payload = {
        "user": "张三",
        "created_at": datetime(2024, 5, 1, 9, 30),
    }

    # 直接 dumps 会报错
    try:
        json.dumps(payload, ensure_ascii=False)
    except TypeError as e:
        print(f"  直接序列化 datetime 报错: {type(e).__name__}: {e}")

    # default: 把不认识的类型转成可序列化的形式
    def encode(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"不支持的类型: {type(obj).__name__}")

    text = json.dumps(payload, ensure_ascii=False, default=encode)
    print(f"  用 default 编码: {text}")

    # object_hook: 反序列化时把 dict 里的字段还原成对象
    def decode(d):
        if "created_at" in d:
            d["created_at"] = datetime.fromisoformat(d["created_at"])
        return d

    obj = json.loads(text, object_hook=decode)
    print(f"  用 object_hook 还原: {obj['created_at']!r}  类型 {type(obj['created_at']).__name__}")

    print("  提示: 传 ISO 字符串是最通用的做法, 跨语言, 跨系统都能认")


# ============================================================
# 3. JSON 读写文件
# ============================================================
def demo_json_file():
    print("--- 3. JSON: 读写文件 ---")

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "config.json"

        config = {"debug": True, "port": 8000, "name": "示例服务"}

        # dump 直接写文件 (要自己管理 encoding, 推荐 with)
        with path.open("w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"  写入 {path.name} ({path.stat().st_size} 字节)")

        # load 直接读文件
        with path.open(encoding="utf-8") as f:
            loaded = json.load(f)
        print(f"  读回: {loaded}")

        # 读-改-写: 最容易踩坑的地方
        loaded["port"] = 9000
        with path.open("w", encoding="utf-8") as f:
            json.dump(loaded, f, ensure_ascii=False, indent=2)
        print(f"  改完再读: {json.loads(path.read_text(encoding='utf-8'))}")


# ============================================================
# 4. CSV 基本用法
# ============================================================
def demo_csv_basic():
    print("--- 4. CSV: writer / DictWriter ---")

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "scores.csv"

        # 写法一: writer 按行写 list
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["name", "score"])
            w.writerows([["张三", 90], ["李四", 85], ["王五", 77]])
        print(f"  writer 写的文件内容:\n{path.read_text(encoding='utf-8')}")

        # 写法二: DictWriter 按字典写 (列顺序由 fieldnames 决定)
        path2 = Path(tmp) / "scores2.csv"
        rows = [
            {"name": "张三", "score": 90},
            {"name": "李四", "score": 85},
        ]
        with path2.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["name", "score"])
            w.writeheader()
            w.writerows(rows)
        print(f"  DictWriter 写的文件内容:\n{path2.read_text(encoding='utf-8')}")

        # 读: reader 得到 list, DictReader 得到 dict
        with path.open(encoding="utf-8") as f:
            print(f"  reader 逐行: {[row for row in csv.reader(f)]}")

        with path.open(encoding="utf-8") as f:
            print("  DictReader 逐行:")
            for row in csv.DictReader(f):
                print(f"    {row}   score 类型是 {type(row['score']).__name__}")

        print("  注意: CSV 读出来全是字符串, 数字要自己 int()/float()")


# ============================================================
# 5. CSV 的编码坑 (Excel 打开乱码)
# ============================================================
def demo_csv_encoding():
    print("--- 5. CSV: utf-8 还是 utf-8-sig ---")

    with tempfile.TemporaryDirectory() as tmp:
        rows = [["name", "城市"], ["张三", "北京"]]

        plain = Path(tmp) / "plain.csv"
        with plain.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(rows)

        bom = Path(tmp) / "with_bom.csv"
        with bom.open("w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerows(rows)

        print(f"  普通 utf-8 前 3 字节: {plain.read_bytes()[:3]}")
        print(f"  utf-8-sig 前 3 字节: {bom.read_bytes()[:3]}   <- EF BB BF 就是 BOM")
        print("  Excel 双击打开 CSV 时按本地编码猜, utf-8 会乱码, utf-8-sig 不会")
        print("  → 要给 Excel 看的文件用 utf-8-sig; 给程序读的用 utf-8")

        # 读的时候用 utf-8-sig 可以自动吃掉 BOM
        with bom.open(encoding="utf-8-sig") as f:
            print(f"  用 utf-8-sig 读回: {list(csv.reader(f))}")


# ============================================================
# 6. 大文件逐行流式处理
# ============================================================
def demo_stream():
    print("--- 6. 大文件: 别一次性读进内存 ---")

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "big.csv"
        n = 50000
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "value"])
            for i in range(n):
                w.writerow([i, i % 100])

        print(f"  生成 {n} 行, 文件 {path.stat().st_size / 1024:.0f} KB")

        # 正确: 逐行迭代, 内存占用恒定
        total, count = 0, 0
        with path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                total += int(row["value"])
                count += 1
        print(f"  流式读取: {count} 行, value 合计 {total}, 平均 {total / count:.1f}")

        # 错误示范: read_text() 一次性载入整个文件
        print(f"  如果 read_text() 会一次性占 {path.stat().st_size / 1024:.0f} KB 内存")
        print("  → 用 with open(...) 或 Path.open() 逐行读, 别 read_text 大文件")


# ============================================================
# 7. 实战: CSV 进, JSON 出
# ============================================================
def demo_use_cases():
    print("--- 7. 实战: 读 CSV 统计, 导出成 JSON 报表 ---")

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "scores.csv"
        src.write_text(
            "name,subject,score\n"
            "张三,数学,90\n"
            "张三,英语,80\n"
            "李四,数学,70\n"
            "李四,英语,95\n",
            encoding="utf-8",
        )

        # 1) 流式读取并聚合
        by_student = {}
        with src.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                item = by_student.setdefault(
                    row["name"], {"name": row["name"], "scores": {}, "total": 0}
                )
                item["scores"][row["subject"]] = int(row["score"])
                item["total"] += int(row["score"])

        # 2) 计算平均分并排序
        report = []
        for item in by_student.values():
            item["avg"] = round(item["total"] / len(item["scores"]), 1)
            report.append(item)
        report.sort(key=lambda x: x["avg"], reverse=True)

        print(f"  聚合结果: {[(r['name'], r['avg']) for r in report]}")

        # 3) 导出 JSON
        out = Path(tmp) / "report.json"
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  导出 {out.name}:")
        for line in out.read_text(encoding="utf-8").splitlines()[:8]:
            print(f"    {line}")

    print("  这条链路 (CSV -> 内存聚合 -> JSON)是数据脚本最常见的形态")


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    import sys
    demos = {
        "json_basic": demo_json_basic,
        "json_types": demo_json_types,
        "json_file": demo_json_file,
        "csv_basic": demo_csv_basic,
        "csv_encoding": demo_csv_encoding,
        "stream": demo_stream,
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
# JSON 四件套:
#   dumps/loads  字符串 <-> 对象 (接口, 日志)
#   dump/load    文件   <-> 对象 (配置)
#   常用参数     ensure_ascii=False (保中文), indent=2 (好看),
#                sort_keys=True (稳定输出, 方便 diff)
#   特殊类型     default= 编码 (datetime -> isoformat), object_hook= 解码
#
# CSV 四件套:
#   DictReader/DictWriter  按列名操作, 别用下标
#   newline=""             写文件必须加, 否则 Windows 多出空行
#   utf-8-sig              给 Excel 看用这个, 普通程序读用 utf-8
#   流式                   大文件用 for row in reader, 不要 read_text
#
# 三个坑:
#   1. CSV 读出来全是 str, "90" 不是 90, 要自己转换
#   2. 写 CSV 不加 newline="" 会在 Windows 上每行多一个空行
#   3. JSON 里没有 datetime/set/自定义类, 要么转字符串, 要么给 default
