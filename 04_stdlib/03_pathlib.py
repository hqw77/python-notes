# ============================================================
# 04. pathlib 模块（现代路径操作）
# ============================================================
# 大纲：
#   - Path 对象创建：Path("."), Path.home(), Path.cwd()
#   - 路径拼接：/ 运算符（比 os.path.join 优雅）
#   - 常用属性：.name, .stem, .suffix, .parent, .parts
#   - 常用方法：.exists(), .is_file(), .is_dir()
#   - 常用方法：.mkdir(), .rmdir(), .unlink(), .rename()
#   - 遍历目录：.iterdir(), .glob(), .rglob()
#   - 文件读写：.read_text(), .write_text(), .read_bytes(), .write_bytes()
#   - pathlib vs os.path（为什么推荐 pathlib）
#   - 获取绝对路径：.resolve(), .absolute()
#   - 文件状态：.stat(), .owner(), .group()
