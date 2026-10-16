# 封装工具类（工程化）

import pymysql
from db_config import DB_CONFIG

class DBHelper:
    def __init__(self):
        self.conn = pymysql.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()

    def query_all(self, sql, args=None):
        self.cursor.execute(sql, args)
        return self.cursor.fetchall()

    def query_one(self, sql, args=None):
        self.cursor.execute(sql, args)
        return self.cursor.fetchone()

    def execute(self, sql, args=None):
        """增删改，自动 commit"""
        try:
            self.cursor.execute(sql, args)
            self.conn.commit()
            return self.cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            raise e

    def close(self):
        self.cursor.close()
        self.conn.close()


# 使用示例
if __name__ == '__main__':
    db = DBHelper()
    print(db.query_all("SELECT * FROM students"))
    db.execute("INSERT INTO students (name, age, email) VALUES (%s, %s, %s)",
               ('测试', 99, 'test@example.com'))
    db.close()