"""
路径参数, 查询参数, 请求体 —— FastAPI 的三种入参方式

【三种传参方式的区别】

  请求 URL:  GET http://localhost:8000/users/5?page=1&size=10
              ├──────────────────┘├┘ ├─────────────┘
              路径参数 (Path)       │   查询参数 (Query)
                              路径参数的值 (5)
                                  查询参数: page=1, size=10

  请求体 (Body): POST/PUT 时把数据放在请求的 body 里 (JSON 格式)

  ┌──────────────┬─────────────────────────┬──────────────────┐
  │ 参数类型      │ 出现在 URL 的哪里?        │ 适合传什么?       │
  ├──────────────┼─────────────────────────┼──────────────────┤
  │ 路径参数      │ URL 路径的一部分           │ 资源 ID          │
  │ (Path)       │ /users/{user_id}         │ /users/5         │
  ├──────────────┼─────────────────────────┼──────────────────┤
  │ 查询参数      │ URL ? 后面的部分          │ 过滤, 排序, 分页  │
  │ (Query)      │ /users?page=1&size=10    │ /search?q=Python  │
  ├──────────────┼─────────────────────────┼──────────────────┤
  │ 请求体        │ HTTP Body (不在 URL 里)   │ 创建/更新的数据    │
  │ (Body)       │ JSON: {"name": "张三"}   │ 注册信息, 文章内容  │
  └──────────────┴─────────────────────────┴──────────────────┘

【FastAPI 如何知道参数类型?】

  - 函数参数在 URL 路径里也有同名占位符 → 路径参数
  - 函数参数是简单类型 (str/int/float/bool) 且不在路径里 → 查询参数
  - 函数参数是 Pydantic 模型 → 请求体
"""

from fastapi import FastAPI

app = FastAPI(title="参数类型演示")


# ============================================================
# 1. 路径参数 (Path Parameter)
# ============================================================

@app.get("/users/{user_id}")
def get_user(user_id: int):         # ← 类型注解自动做类型转换!
    """
    访问 /users/5  → user_id = 5 (int)
    访问 /users/abc → FastAPI 自动返回 422 错误 (不是 int)
    """
    return {
        "message": f"获取用户 {user_id}",
        "user_id": user_id,
        "type": str(type(user_id).__name__),  # → "int"
    }


@app.get("/items/{item_id}")
def get_item(item_id: int):
    """多一个路径参数"""
    return {"item_id": item_id}


# ============================================================
# 2. 查询参数 (Query Parameter)
# ============================================================

# 模拟数据库
fake_users = [
    {"id": 1, "name": "张三", "age": 25, "city": "北京"},
    {"id": 2, "name": "李四", "age": 30, "city": "上海"},
    {"id": 3, "name": "王五", "age": 28, "city": "北京"},
    {"id": 4, "name": "赵六", "age": 22, "city": "深圳"},
]

@app.get("/users")                   # 注意: 路径里没有 {page}
def list_users(
    page: int = 1,                   # 查询参数: ?page=1
    size: int = 10,                  # 查询参数: ?size=10
    city: str | None = None,         # 可选查询参数: ?city=北京
):
    """
    访问 /users?page=1&size=10
    访问 /users?page=2&size=5&city=北京
    """
    # 手动筛选
    result = fake_users
    if city:
        result = [u for u in result if u["city"] == city]

    # 手动分页
    start = (page - 1) * size
    paged = result[start:start + size]

    return {
        "page": page,
        "size": size,
        "total": len(result),
        "data": paged,
    }


# ============================================================
# 3. 路径参数 + 查询参数 组合
# ============================================================

@app.get("/users/{user_id}/posts")
def get_user_posts(
    user_id: int,                    # 路径参数
    limit: int = 5,                  # 查询参数 ?limit=5
    published: bool = True,          # 查询参数 ?published=true
):
    """
    访问 /users/5/posts?limit=10&published=true
    user_id 来自路径, limit 和 published 来自 ? 后面的查询参数
    """
    return {
        "user_id": user_id,
        "limit": limit,
        "published": published,
        "posts": [f"用户 {user_id} 的帖子 {i}" for i in range(1, limit + 1)],
    }


# ============================================================
# 4. 类型校验: 自动的!
# ============================================================

@app.get("/calc")
def calc(a: int, b: int, op: str = "add"):
    """
    访问 /calc?a=3&b=5&op=add  → {"result": 8}
    访问 /calc?a=3&b=5&op=mul  → {"result": 15}
    访问 /calc?b=5&op=add        → FastAPI 返回错误: a 是必填的!
    访问 /calc?a=abc&b=5         → FastAPI 返回错误: a 必须是 int!
    """
    if op == "add":
        result = a + b
    elif op == "mul":
        result = a * b
    else:
        result = 0
    return {"a": a, "b": b, "op": op, "result": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
