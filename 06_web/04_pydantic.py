"""
Pydantic 数据模型 —— 请求体的类型校验

【Pydantic 是什么?】

  你写一个 API, 用户传数据进来. 怎么保证数据格式正确?
  传统写法: if not isinstance(...): raise ... 一大堆判断
  Pydantic: 定义一个类, 字段类型写清楚, 自动校验

  Pydantic 类很像你学过的 dataclass, 但 Pydantic 专为数据校验设计:
    - dataclass: 省 __init__ 样板代码
    - Pydantic: 省 __init__ + 类型校验 + 错误提示 + JSON 转换

【FastAPI 怎么用 Pydantic?】

  当你把函数参数声明为 Pydantic 模型, FastAPI 自动:
    1. 从请求体读取 JSON
    2. 用 Pydantic 模型校验类型
    3. 把校验通过的数据作为参数传给函数
    4. 校验失败自动返回 422 错误
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(title="Pydantic 模型演示")


# ============================================================
# 1. 定义 Pydantic 模型
# ============================================================
# Pydantic 模型 = 数据的"模板", 和 JSON 直接互转

class User(BaseModel):
    """用户数据模型"""
    name: str                              # 必填, 必须是 str
    age: int = Field(ge=0, le=150)         # 0-150 之间
    email: str | None = None               # 可选, 默认 None
    skills: list[str] = []                 # 默认空列表


class CreateResponse(BaseModel):
    """创建成功的响应"""
    message: str
    user_id: int


# ============================================================
# 2. 请求体 (Request Body) —— POST 创建用户
# ============================================================

@app.post("/users", response_model=CreateResponse)
def create_user(user: User):               # ← user 声明为 Pydantic 模型!
    """
    客户端 POST /users, body 为 JSON:
      {"name": "张三", "age": 25, "email": "test@example.com"}

    FastAPI 自动:
      1. 读 body → JSON → Pydantic User 对象
      2. 校验: name 必填, age 0-150, email 可选
      3. 校验失败 → 自动返回 422 错误, 告诉你哪个字段不对
    """
    print(f"  收到用户: {user.model_dump()}")   # 转成 dict
    # 模拟创建
    return CreateResponse(message=f"用户 {user.name} 创建成功", user_id=999)


# ============================================================
# 3. 数据校验在起作用 —— 试试传错误数据
# ============================================================

# 试试 POST /users, body: {"name": "张三"}
# → age 必填, 返回 422:
# {
#   "detail": [{
#     "type": "missing",
#     "loc": ["body", "age"],
#     "msg": "Field required"
#   }]
# }

# 试试 POST /users, body: {"name": "张三", "age": 999}
# → age > 150, 返回 422:
# {
#   "detail": [{
#     "type": "less_than_equal",
#     "loc": ["body", "age"],
#     "msg": "Input should be less than or equal to 150"
#   }]
# }


# ============================================================
# 4. Pydantic 进阶: 嵌套模型
# ============================================================

class Address(BaseModel):
    """嵌套的子模型"""
    city: str
    street: str = ""
    zipcode: str | None = None

class UserWithAddress(BaseModel):
    name: str
    age: int
    address: Address                    # ← 嵌套另一个 Pydantic 模型!

@app.post("/users/with-address")
def create_user_with_address(user: UserWithAddress):
    """
    请求体:
    {
      "name": "张三",
      "age": 25,
      "address": {
        "city": "北京",
        "street": "长安街"
      }
    }
    """
    return {
        "message": f"{user.name} 创建成功",
        "city": user.address.city,
    }


# ============================================================
# 5. Pydantic 和 Python dict 的互转
# ============================================================

@app.get("/pydantic-demo")
def pydantic_demo():
    """演示 Pydantic 对象的常用操作"""
    # dict → Pydantic
    raw = {"name": "张三", "age": 25}
    user = User(**raw)                   # 等价于 User(name="张三", age=25)

    # Pydantic → dict
    d = user.model_dump()                # → {"name": "张三", "age": 25, ...}

    # Pydantic → JSON 字符串
    j = user.model_dump_json()           # → '{"name":"张三","age":25,...}'

    return {
        "from_dict": d,
        "to_json": j,
    }


# ============================================================
# 总结
# ============================================================
# - Pydantic 模型用 BaseModel 定义
# - 字段类型注解 = 校验规则
# - Field() 可加额外约束 (ge, le, min_length, pattern 等)
# - FastAPI 自动把 JSON 请求体转成 Pydantic 对象
# - 校验失败自动返回 422, 不用手写 if/raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
