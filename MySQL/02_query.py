# SQL 查询

from db_config import get_conn

conn = get_conn()
cursor = conn.cursor()

# 1. 查询全部
cursor.execute("SELECT id, name, age, email FROM students")
print("全部：", cursor.fetchall())

# 2. 条件查询
cursor.execute("SELECT * FROM students WHERE age > 20")
print("age > 20:", cursor.fetchall())

# 3. 排序
cursor.execute("SELECT * FROM students ORDER BY age DESC")
print("按年龄降序:", cursor.fetchall())

# 4. 限制条数
cursor.execute("SELECT * FROM students LIMIT 2")
print("前2条:", cursor.fetchall())

# 5. 聚合
cursor.execute("SELECT COUNT(*), AVG(age), MAX(age), MIN(age) FROM students")
print("统计:", cursor.fetchall())

# 6. 分组
cursor.execute("SELECT age, COUNT(*) FROM students GROUP BY age")
print("年龄分组:", cursor.fetchall())

# 7. 模糊查询
cursor.execute("SELECT * FROM students WHERE name LIKE '张%'")
print("姓张:", cursor.fetchall())

cursor.close()
conn.close()