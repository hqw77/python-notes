# 从 .env 读取配置，避免密码硬编码

import os
import pymysql
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'charset': 'utf8mb4'
}

print("读取到的配置:", DB_CONFIG)

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM students")
print("学生总数:", cursor.fetchone()[0])

cursor.close()
conn.close()