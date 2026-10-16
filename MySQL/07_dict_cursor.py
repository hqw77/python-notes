# DictCursor：让查询结果返回字典而不是元组

import pymysql
from db_config import DB_CONFIG

# 注意：连接时传 cursorclass 参数
conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

# 查询：返回的是 dict
cursor.execute("SELECT id, name, age, email FROM students")
rows = cursor.fetchall()
print("类型:", type(rows[0]))     # <class 'dict'>
for row in rows:
    print(row)

# 取字段更直观
print("\n--- 按字段取值 ---")
cursor.execute("SELECT * FROM students WHERE age > 20")
for row in cursor.fetchall():
    print(f"{row['name']} 今年 {row['age']} 岁，邮箱 {row['email']}")

# JOIN 查询：dict 的优势立刻显现
print("\n--- JOIN 查询（字典更易读）---")
cursor.execute("""
    SELECT s.name AS student, c.name AS course, e.score
    FROM enrollments e
    JOIN students s ON e.student_id = s.id
    JOIN courses c ON e.course_id = c.id
    ORDER BY e.score DESC
""")
for row in cursor.fetchall():
    print(f"{row['student']} 选了 {row['course']}，成绩 {row['score']}")

cursor.close()
conn.close()