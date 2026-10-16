# 连接mysql

import pymysql

# 连接数据库
conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='123456',
    database='py_adv_db',      # 注意这里改成你刚建的库
    charset='utf8mb4'
)

cursor = conn.cursor()

# 查询刚才插入的数据
cursor.execute("SELECT id, name, age, email FROM students")
rows = cursor.fetchall()

print("查询结果：")
for row in rows:
    print(row)

# 关闭资源
cursor.close()
conn.close()
print("\n连接已关闭")
