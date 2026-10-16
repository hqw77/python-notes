# 参数化插入

from db_config import get_conn

conn = get_conn()
cursor = conn.cursor()

# 单条插入：用 %s 占位符（不是 ?，不是 f-string！）
sql = "INSERT INTO students (name, age, email) VALUES (%s, %s, %s)"
cursor.execute(sql, ('赵六', 23, 'zhaoliu@example.com'))

# 批量插入
sql = "INSERT INTO students (name, age, email) VALUES (%s, %s, %s)"
data = [
    ('孙七', 24, 'sunqi@example.com'),
    ('周八', 25, 'zhouba@example.com'),
]
cursor.executemany(sql, data)

# ⚠️ 关键：增删改必须 commit，否则数据不落盘
conn.commit()

print("插入成功，影响行数:", cursor.rowcount)

cursor.close()
conn.close()
