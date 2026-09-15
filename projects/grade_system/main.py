"""
学生成绩管理系统 —— 主程序

用到的知识:
  01_basic:  while 循环菜单, if/elif 分支, f-string, 列表/字典操作
  02_oop:    创建 Student 实例, 调用方法, @property 读取平均分
  03_advanced: for 遍历容器, sorted 排序, 生成器表达式筛选
  03_advanced: 装饰器 (save/load 自动日志)
"""

from models import Student, GradeManager
from storage import save, load


# ============================================================
# 菜单逻辑
# ============================================================
def show_menu():
    """打印主菜单"""
    print("\n" + "=" * 40)
    print("       学生成绩管理系统")
    print("=" * 40)
    print("  1. 添加学生")
    print("  2. 录入成绩")
    print("  3. 查看所有学生")
    print("  4. 查看排名 (前 5)")
    print("  5. 筛选及格 / 不及格")
    print("  6. 班级概况")
    print("  7. 删除学生")
    print("  8. 保存到文件")
    print("  9. 从文件加载")
    print("  0. 退出")
    print("-" * 40)


def add_student(manager):
    """功能 1: 添加学生"""
    name = input("  学生姓名: ").strip()
    if not name:
        print("  ⚠ 姓名不能为空")
        return
    if manager.find(name):
        print(f"  ⚠ 学生 '{name}' 已存在")
        return
    manager.add(Student(name))
    print(f"  ✓ 已添加 '{name}'")


def input_scores(manager):
    """功能 2: 录入成绩"""
    name = input("  学生姓名: ").strip()
    student = manager.find(name)
    if not student:
        print(f"  ⚠ 没有叫 '{name}' 的学生, 请先添加")
        return

    print(f"  当前 {student}")
    raw = input("  输入成绩 (多个用逗号分隔, 如 85,90,78): ")
    try:
        for s in raw.split(","):
            student.add_score(float(s.strip()))
    except ValueError:
        print("  ⚠ 成绩格式不对")
        return
    print(f"  ✓ 录入完毕, {student}")


def show_all(manager):
    """功能 3: 查看所有学生 —— 让 for 用上容器协议!"""
    if len(manager) == 0:      # 这里调了 __len__
        print("  暂无学生")
        return
    # 这里的 for 用了 __getitem__ 或 __iter__
    for i, student in enumerate(manager, 1):
        print(f"  [{i}] {student}")          # print 调了 __str__


def show_rank(manager):
    """功能 4: 排名 —— 让 sorted 用上 __lt__!"""
    if len(manager) == 0:
        print("  暂无学生")
        return
    print("  前 5 名:")
    # sorted 内部调了 Student.__lt__, rank 方法我们写在 models 里
    for i, s in enumerate(manager.top_n(5), 1):
        print(f"    [{i}] {s}")


def filter_students(manager):
    """功能 5: 筛选及格/不及格"""
    print("  1. 查看及格 (≥60)")
    print("  2. 查看不及格 (<60)")
    choice = input("  选择: ").strip()

    if choice == "1":
        # 列表推导式返回 list
        passed = manager.filter_passed()
        print(f"  及格人数: {len(passed)}")
        for s in passed:
            print(f"    {s}")
    elif choice == "2":
        # 生成器表达式返回 generator
        failed = manager.filter_failed()
        # 用 list() 把生成器转成列表, 因为生成器只能消费一次
        failed_list = list(failed)
        print(f"  不及格人数: {len(failed_list)}")
        for s in failed_list:
            print(f"    {s}")


def show_summary(manager):
    """功能 6: 班级概况"""
    print(manager.summary())


def remove_student(manager):
    """功能 7: 删除学生"""
    name = input("  要删除的学生姓名: ").strip()
    try:
        s = manager.remove(name)
        print(f"  ✓ 已删除 '{s.name}'")
    except KeyError as e:
        print(f"  ⚠ {e}")


def save_data(manager):
    """功能 8: 保存"""
    save(manager)


def load_data(manager):
    """功能 9: 加载 —— 用新的数据替换当前班级里的学生"""
    students = load()
    manager._students = students          # 直接替换内部列表
    print(f"  班级现有 {len(manager)} 名学生")


# ============================================================
# 主循环
# ============================================================
def main():
    manager = GradeManager("Python 学习班")
    # 预置一些示例数据
    for name, scores in [
        ("张三", [85, 90, 78]),
        ("李四", [92, 88, 95]),
        ("王五", [60, 55, 58]),
        ("赵六", [72, 68, 75]),
    ]:
        s = Student(name, scores)
        manager.add(s)

    print(f"  已预置 4 名学生的示例数据, 可直接操作")

    menu_actions = {
        "1": add_student,
        "2": input_scores,
        "3": show_all,
        "4": show_rank,
        "5": filter_students,
        "6": show_summary,
        "7": remove_student,
        "8": save_data,
        "9": load_data,
    }

    while True:
        show_menu()
        choice = input("  请输入选项: ").strip()

        if choice == "0":
            print("  再见!")
            break
        elif choice in menu_actions:
            try:
                menu_actions[choice](manager)
            except Exception as e:
                print(f"  ✗ 出错: {e}")
        else:
            print(f"  ⚠ 无效选项 '{choice}', 请重试")


if __name__ == "__main__":
    main()
