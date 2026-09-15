"""
完整 CRUD API —— 增删改查

CRUD = Create, Read, Update, Delete

这是后端最核心的四种操作. 每一个数据表都要写这四个接口.

  Method   URL              功能
  POST     /students         创建学生 (Create)
  GET      /students         查看所有 (Read - List)
  GET      /students/{id}    查看单个 (Read - Detail)
  PUT      /students/{id}    更新学生 (Update)
  DELETE   /students/{id}    删除学生 (Delete)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional


app = FastAPI(title="学生 CRUD API")


# ============================================================
# 1. 定义模型
# ============================================================

class StudentCreate(BaseModel):
    """创建学生时传入的参数"""
    name: str
    age: int
    course: str = "Python"


class StudentUpdate(BaseModel):
    """更新学生时的参数, 所有字段可选 (只更新传了的)"""
    name: Optional[str] = None
    age: Optional[int] = None
    course: Optional[str] = None


class Student(BaseModel):
    """学生的完整信息 (包括自动生成的 id)"""
    id: int
    name: str
    age: int
    course: str


# ============================================================
# 2. 模拟数据库 (内存版, 后面换成 SQLAlchemy)
# ============================================================
fake_db: list[Student] = []
next_id = 1

# 初始化几条示例数据
for name, age, course in [
    ("张三", 20, "Python"),
    ("李四", 22, "FastAPI"),
    ("王五", 21, "Python"),
]:
    fake_db.append(Student(id=next_id, name=name, age=age, course=course))
    next_id += 1


# ============================================================
# 3. CRUD 接口
# ============================================================

# ---------- Create (POST) ----------

@app.post("/students", response_model=Student, status_code=201)
def create_student(data: StudentCreate):
    """
    创建新学生, POST /students
    Body: {"name": "赵六", "age": 23, "course": "Django"}

    返回 201 Created + 新创建的学生对象
    """
    global next_id
    student = Student(id=next_id, **data.model_dump())
    fake_db.append(student)
    next_id += 1
    return student


# ---------- Read - List (GET all) ----------

@app.get("/students", response_model=list[Student])
def list_students(course: Optional[str] = None):
    """
    查看所有学生, GET /students
    可选筛选: GET /students?course=Python
    """
    if course:
        return [s for s in fake_db if s.course == course]
    return fake_db


# ---------- Read - Detail (GET one) ----------

@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    """
    查看单个学生, GET /students/1
    查不到返回 404
    """
    for s in fake_db:
        if s.id == student_id:
            return s
    raise HTTPException(status_code=404, detail=f"学生 {student_id} 不存在")


# ---------- Update (PUT) ----------

@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, data: StudentUpdate):
    """
    更新学生, PUT /students/1
    Body: {"age": 24}  (只改年龄, 其他不动)
    """
    for s in fake_db:
        if s.id == student_id:
            # 只更新传了的字段
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(s, key, value)        # 动态设置属性
            return s
    raise HTTPException(status_code=404, detail=f"学生 {student_id} 不存在")


# ---------- Delete (DELETE) ----------

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    """
    删除学生, DELETE /students/1
    """
    for i, s in enumerate(fake_db):
        if s.id == student_id:
            deleted = fake_db.pop(i)
            return {"message": f"学生 {deleted.name} (id={student_id}) 已删除"}
    raise HTTPException(status_code=404, detail=f"学生 {student_id} 不存在")


# ============================================================
# 总结
# ============================================================
# CRUD 套路:
#   POST   /资源               → 创建, 返回 201
#   GET    /资源               → 列表, 可加筛选
#   GET    /资源/{id}          → 单个, 查不到返回 404
#   PUT    /资源/{id}          → 更新, 只改传了的字段
#   DELETE /资源/{id}          → 删除, 返回成功信息
#
# 这个套路几乎每一个数据表都要写一遍, 后面用数据库时会改成持久化的.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
