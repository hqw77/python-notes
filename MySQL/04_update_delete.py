# 更新 & 删除

from db_config import get_conn

conn = get_conn()
cursor = conn.cursor()

# 更新
cursor.execute("UPDATE students SET age = %s WHERE name = %s", (30, '赵六'))
print("更新影响行数:", cursor.rowcount)

# 删除
cursor.execute("DELETE FROM students WHERE name = %s", ('周八',))
print("删除影响行数:", cursor.rowcount)


# 同样必须 commit
conn.commit()

cursor.close()
conn.close()