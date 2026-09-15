# Python Web 后端学习路线 (FastAPI)

## 学习路径

```
01_http_basics.py     → HTTP 是什么, 请求/响应结构
02_fastapi_hello.py   → 第一个 API, 运行服务
03_params.py          → 路径参数, 查询参数, 请求体
04_pydantic.py        → Pydantic 数据模型, 类型校验
05_crud.py            → 完整的增删改查 API
06_database.py        → SQLAlchemy + SQLite 数据库
07_auth.py            → JWT 登录认证
```

## 运行方式

```bash
# 激活虚拟环境 (PowerShell)
.\.venv\Scripts\Activate.ps1

# 或直接用虚拟环境的 Python
.venv\Scripts\python.exe 06_web/02_fastapi_hello.py

# 访问 http://localhost:8000 查看结果
# 访问 http://localhost:8000/docs 查看自动生成的文档
```

## 所有 API 的共同结构

```
用户请求 (Request)
    ↓
FastAPI 路由匹配 URL → 校验入参 (Pydantic)
    ↓
你的函数执行业务逻辑 (查数据库, 计算, ...)
    ↓
返回结果 (Response, 通常是 JSON)
```

## 和已学知识的关联

| Web 概念 | 用到你学过的什么 |
|---|---|
| FastAPI 路由装饰器 | `06_decorator.py` → `@app.get("/")` 就是装饰器 |
| Pydantic 模型 | `07_descriptor.py` → 字段验证底层是描述符 |
| SQLAlchemy ORM | `02_oop` → 类和表映射; `07_descriptor.py` → Column 是描述符 |
| 异步处理 | `10_async_basics.py` → `async def`, `await` |
| 类型校验 | `05_tooling/03_type_hints.py` → FastAPI 全是类型注解驱动 |
