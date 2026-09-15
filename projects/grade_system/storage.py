"""
数据持久化 —— 把成绩存到磁盘, 下次打开还有

用到的知识:
  01_basic:  JSON 文件读写, dict 操作
  03_advanced: 装饰器 (记录操作日志)
"""

import json
import os
from functools import wraps


def log_action(func):
    """装饰器: 每次调用 save/load 时自动打印时间戳"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"  [日志] {func.__name__} 完成, 耗时 {elapsed:.4f}s")
        return result
    return wrapper


@log_action
def save(manager, filepath="grade_data.json"):
    """
    把 GradeManager 里的所有学生存为 JSON 文件.

    JSON 格式:
    [
      {"name": "张三", "scores": [85, 90, 78]},
      {"name": "李四", "scores": [92, 88]}
    ]
    """
    data = []
    for student in manager:
        data.append({
            "name": student.name,
            "scores": student.scores,    # 注意: 这里用了我们之前定义的 @property
        })

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  已保存 {len(data)} 名学生到 {filepath}")


@log_action
def load(filepath="grade_data.json"):
    """
    从 JSON 文件读取数据, 重建 Student 列表.

    注: 这里要导入 models 里的 Student, 否则不知道这个类.
    """
    from models import Student

    if not os.path.exists(filepath):
        print(f"  文件 {filepath} 不存在, 返回空")
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    students = []
    for item in raw_data:
        student = Student(item["name"], item.get("scores", []))
        students.append(student)

    print(f"  已从 {filepath} 加载 {len(students)} 名学生")
    return students
