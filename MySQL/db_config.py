# db_config.py
import pymysql

# 数据库连接配置（统一放这里，改一处即可）
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'py_adv_db',
    'charset': 'utf8mb4'
}

def get_conn():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)