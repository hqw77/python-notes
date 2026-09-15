# ============================================================
# 07. JSON 与 CSV 处理
# ============================================================
# 大纲：
#   - JSON：
#     - json.dumps()：Python → JSON 字符串
#     - json.dump()：Python → JSON 文件
#     - json.loads()：JSON 字符串 → Python
#     - json.load()：JSON 文件 → Python
#     - 类型映射：dict↔object, list↔array, str↔string, int/float↔number
#     - indent 参数美化输出
#     - ensure_ascii=False 处理中文
#     - default 参数处理不可序列化对象（如 datetime）
#     - object_hook 参数自定义反序列化
#   - CSV：
#     - csv.reader() / csv.writer()
#     - csv.DictReader() / csv.DictWriter()（推荐，用字典操作）
#     - 指定分隔符：delimiter=','
#     - 处理表头
#     - 编码问题（utf-8-sig 处理 BOM）
#     - 大文件逐行处理
