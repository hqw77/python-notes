"""
SQLAlchemy + SQLite —— 数据库持久化

【为什么需要数据库?】

  之前 fake_db = [] 存在内存里, 程序关了就没了.
  数据库让数据保存到磁盘上, 程序关了数据还在.

【SQLAlchemy 是什么?】

  SQLAlchemy 是 Python 最流行的 ORM (Object-Relational Mapping).
  ORM 让你用 Python 类操作数据库表, 不用写 SQL.

  你的 Python 类      数据库表
  ──────────────     ──────────
  class Student  →   students 表
  s.name = "张三" →   INSERT INTO students ...
  s.age = 20      →   UPDATE students SET age=20 ...

【SQLite 是什么?】

  一个轻量级数据库, 数据存在一个 .db 文件里.
  不需要安装数据库软件, Python 自带 sqlite3 模块.
  适合学习和小项目. 生产环境一般用 PostgreSQL.

【你在 02_oop 和 03_advanced 学的知识, 这里全用上了】

  - ORM 模型就是 OOP 类
  - SQLAlchemy 的 Column, relationship 底层就是描述符协议
  - FastAPI + SQLAlchemy 的组合就是类型注解 + 描述符的完美应用
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from pydantic import ConfigDict

# SQLAlchemy 导入
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# ============================================================
# 1. 初始化数据库连接
# ============================================================
# SQLite 数据库文件:  student.db (程序跑完后会出现在当前目录)
import os
DB_PATH = os.path.join(os.path.dirname(__file__), "student.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 需要这个参数
)

# SessionLocal = 会话工厂, 每次请求创建一个新会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ============================================================
# 2. 定义 ORM 模型 (就是 Python 类!)
# ============================================================
class Base(DeclarativeBase):
    """所有 ORM 模型的基类"""
    pass


class StudentORM(Base):
    """
    学生表 —— 和 05_crud.py 里的 Pydantic Student 不同:
    - Pydantic 模型: 定义 API 的输入输出格式
    - SQLAlchemy 模型: 定义数据库表结构
    """
    __tablename__ = "students"       # 对应的数据库表名

    id = Column(Integer, primary_key=True, index=True)   # 主键, 自增
    name = Column(String, nullable=False)                # 非空
    age = Column(Integer, nullable=False)
    course = Column(String, default="Python")

    def __repr__(self):
        return f"<Student(id={self.id}, name={self.name!r})>"


# ============================================================
# 3. 创建表 (只在第一次运行时创建, 已存在就跳过)
# ============================================================
Base.metadata.create_all(bind=engine)


# ============================================================
# 4. FastAPI 应用
# ============================================================
app = FastAPI(title="学生 CRUD (数据库版)")


# ---------- 依赖注入: 获取数据库会话 ----------
def get_db():
    """
    每个请求自动创建数据库会话, 请求结束后自动关闭.
    这里用了生成器: yield 之前 = __enter__, yield 之后 = __exit__
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Pydantic 模型 (和 05_crud 一样) ----------
class StudentCreate(BaseModel):
    name: str
    age: int
    course: str = "Python"

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    course: Optional[str] = None

class StudentOut(BaseModel):
    """返回给客户端的学生数据"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    age: int
    course: str


# ============================================================
# 5. CRUD 接口 (数据库版)
# ============================================================

@app.post("/students", response_model=StudentOut, status_code=201)
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    """创建学生 —— 现在真的存到数据库了!"""
    db_student = StudentORM(**data.model_dump())
    db.add(db_student)             # INSERT INTO students ...
    db.commit()                     # 提交事务
    db.refresh(db_student)          # 刷新, 拿到数据库生成的 id
    return db_student


@app.get("/students", response_model=list[StudentOut])
def list_students(course: Optional[str] = None, db: Session = Depends(get_db)):
    """查看所有学生 —— 从数据库查"""
    if course:
        return db.query(StudentORM).filter(StudentORM.course == course).all()
    return db.query(StudentORM).all()


@app.get("/students/{student_id}", response_model=StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """查看单个学生"""
    s = db.query(StudentORM).filter(StudentORM.id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail=f"学生 {student_id} 不存在")
    return s


@app.put("/students/{student_id}", response_model=StudentOut)
def update_student(student_id: int, data: StudentUpdate, db: Session = Depends(get_db)):
    """更新学生"""
    s = db.query(StudentORM).filter(StudentORM.id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail=f"学生 {student_id} 不存在")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(s, key, value)
    db.commit()
    db.refresh(s)
    return s


@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """删除学生"""
    s = db.query(StudentORM).filter(StudentORM.id == student_id).first()
    if not s:
        raise HTTPException(status_code=404, detail=f"学生 {student_id} 不存在")
    db.delete(s)
    db.commit()
    return {"message": f"学生 {s.name} (id={student_id}) 已删除"}


# ============================================================
# 总结
# ============================================================
# ORM 核心操作:
#   db.add(obj)    → INSERT
#   db.commit()    → 提交事务 (增删改都要)
#   query.all()    → SELECT * (查所有)
#   query.filter() → SELECT ... WHERE ... (条件查询)
#   db.delete(obj) → DELETE
#   db.refresh(obj)→ 拿到数据库生成的值 (如 id)
#
# Depends(get_db) 的作用:
#   每个请求自动获取一个新的数据库会话,
#   请求处理完自动关闭. 本质是生成器的 yield 机制.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
