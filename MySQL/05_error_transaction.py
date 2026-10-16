from db_config import get_conn

conn = get_conn()
cursor = conn.cursor()

print("autocommit =", conn.get_autocommit())   # 应为 False

try:
    # 查操作前状态
    cursor.execute("SELECT age FROM students WHERE name = %s", ('张三',))
    before = cursor.fetchone()
    print("操作前张三 age:", before)

    # 第一条：正常更新
    cursor.execute("UPDATE students SET age = age + 1 WHERE name = %s", ('张三',))

    # 第二条：故意报错（email 重复，违反 UNIQUE 约束）
    cursor.execute(
        "INSERT INTO students (name, age, email) VALUES (%s, %s, %s)",
        ('李四副本', 25, 'lisi@example.com')
    )

    conn.commit()
    print("✅ 事务提交")

except Exception as e:
    conn.rollback()
    print("❌ 异常，已回滚：", e)

finally:
    # 查操作后状态
    cursor.execute("SELECT age FROM students WHERE name = %s", ('张三',))
    after = cursor.fetchone()
    print("操作后张三 age:", after)

    cursor.close()
    conn.close()