"""
FastAPI 快速入门 —— 第一个 Web API

【FastAPI 是什么?】

  一个现代 Python Web 框架, 核心特征:
  - 快: 性能对标 Node.js/Go
  - 类型注解驱动: 你刚学的 type hints 在这里是核心功能
  - 自动生成文档: 访问 /docs 就能看到交互式 API 文档
  - 异步支持: 原生支持 async/await

【运行方式】

  # 方式 1: 直接用 uvicorn 命令
  uvicorn 02_fastapi_hello:app --reload

  # 方式 2: 在代码里启 (这个文件直接跑)
  python 02_fastapi_hello.py

  然后浏览器访问:
    http://localhost:8000       → 返回 JSON
    http://localhost:8000/docs  → 自动生成的 Swagger 文档

  按 Ctrl+C 停止服务器.
"""

from fastapi import FastAPI

# ============================================================
# 1. 创建应用实例
# ============================================================
# FastAPI() 就是你的 Web 应用的入口.
app = FastAPI(
    title="我的第一个 API",
    description="FastAPI 学习项目",
    version="1.0.0",
)

# ============================================================
# 2. 定义路由 —— @app.get() 就是装饰器!
# ============================================================
# 回忆 06_decorator.py: @decorator 把下面的函数注册起来
# @app.get("/") 也一样: 把下面的函数注册为处理 GET / 请求

@app.get("/")
def root():
    """访问 http://localhost:8000/ 时执行这个函数"""
    return {"message": "Hello, FastAPI!", "status": "ok"}


@app.get("/hello/{name}")
def say_hello(name: str):
    """访问 http://localhost:8000/hello/张三 时执行"""
    # name 自动从 URL 里提取, 类型自动校验
    return {"greeting": f"Hello, {name}!"}


@app.get("/status")
def status():
    """访问 http://localhost:8000/status"""
    return {
        "app": "FastAPI 学习",
        "version": "1.0.0",
        "learned": ["02_oop", "03_advanced", "05_tooling"],
    }


# ============================================================
# 3. 启动服务
# ============================================================
if __name__ == "__main__":
    import uvicorn
    # host="0.0.0.0"   → 允许局域网其他设备访问
    # port=8000        → 端口号
    # reload=True      → 代码改了自动重启 (开发模式)
    uvicorn.run(app, host="127.0.0.1", port=8000)

# ============================================================
# 动手试试:
#   1. 运行这个文件
#   2. 浏览器打开 http://localhost:8000
#   3. 打开 http://localhost:8000/docs 看看 Swagger 文档
#   4. 打开 http://localhost:8000/hello/你的名字
#   5. 在 /docs 页面试用 "Try it out" 按钮
# ============================================================
