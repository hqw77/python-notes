import time
import asyncio
from functools import wraps
from typing import Callable, Any
from pydantic import BaseModel, Field, ValidationError

# ==========================================
# 1. 工具注册表（核心）
# ==========================================
class Agent:
    def __init__(self, name: str):
        self.name = name
        self._tools: dict[str, dict] = {}

    def tool(self, name: str, description: str):
        """装饰器：把函数注册进 Agent"""
        def decorator(func: Callable):
            self._tools[name] = {          # 把工具的全部信息存进注册表，键是工具名
                "func": func,              # 函数本体，调用时用
                "description": description,# 描述，给模型看
                "schema": getattr(func, "__schema__", None),  # 参数结构，给模型看
            }
            return func                    # 原样返回函数，只登记不改变行为
        return decorator

    def list_tools(self):
        return [
            {"name":n, "description": t["description"]}
            for n, t in self._tools.items()
        ]

    async def call(self, name: str, **kwargs):
        """统一调用入口"""
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"工具 {name} 不存在")
        return await tool["func"](**kwargs)

# ==========================================
# 2. 装饰器：日志计时
# ==========================================
def log_time(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        print(f"[LOG] 开始执行 {func.__name__}，参数: {kwargs}")
        try:
            result = await func(*args, **kwargs)
            print(f"[LOG] {func.__name__} 完成，耗时 {time.time()-start:.2f}s")
            return result
        except Exception as e:
            print(f"[LOG] {func.__name__} 失败: {e}，耗时 {time.time()-start:.2f}s")
            raise
    return wrapper

# ==========================================
# 3. 装饰器：参数校验（基于 Pydantic）
# ==========================================
def validate_params(schema: type[BaseModel]):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                validated = schema(**kwargs)
                return await func(*args, **validated.model_dump())
            except ValidationError as e:
                # 把校验错误转成模型可读的提示，方便回传给 LLM
                raise ValueError(f"参数校验失败: {e.errors()}")
        return wrapper
    return decorator

# ==========================================
# 4. 装饰器：自动重试
# ==========================================
def retry(max_attempts: int = 3, delay: float = 0.5):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_err = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_err = e
                    print(f"[RETRY] {func.__name__} 第 {attempt} 次失败: {e}")
                    if attempt < max_attempts:
                        await asyncio.sleep(delay)
            raise last_err
        return wrapper
    return decorator


# ==========================================
# 5. 定义工具的参数 Schema
# ==========================================
class SearchInput(BaseModel):
    query: str = Field(..., min_length=1, description="搜索关键词")
    top_k: int = Field(default=3, ge=1, le=10, description="返回条数")


class RefundInput(BaseModel):
    order_id: str = Field(..., pattern=r"^ORD-\d+$", description="订单号")
    reason: str = Field(..., min_length=2, description="退款原因")

# ==========================================
# 6. 创建 Agent 并注册工具（装饰器堆叠）
# ==========================================
agent = Agent("客服助手")


@agent.tool("search", "搜索网络")
@log_time
@validate_params(SearchInput)
@retry(max_attempts=3)
async def search(query: str, top_k: int = 3):
    """模拟搜索工具"""
    if "fail" in query:
        raise RuntimeError("模拟网络抖动")
    await asyncio.sleep(0.2)
    return f"搜索「{query}」，返回 {top_k} 条结果"

@agent.tool("refund", "申请退款")
@log_time
@validate_params(RefundInput)
async def refund(order_id: str, reason: str):
    """模拟退款工具"""
    await asyncio.sleep(0.1)
    return f"订单 {order_id} 退款申请已提交，原因：{reason}"

# ==========================================
# 7. 运行测试
# ==========================================
async def main():
    print("已注册工具:", agent.list_tools())
    print()

    print("--- 正常调用 search ---")
    print(await agent.call("search", query="LangGraph 教程", top_k=5))
    print()

    print("--- 参数不合法（top_k 超出范围）---")
    try:
        await agent.call("search", query="test", top_k=99)
    except ValueError as e:
        print("拦截:", e)
    print()

    print("--- 触发重试（query 含 fail）---")
    try:
        await agent.call("search", query="fail_case")
    except Exception as e:
        print("最终失败:", e)
    print()

    print("--- 正常调用 refund ---")
    print(await agent.call("refund", order_id="ORD-123", reason="质量问题"))
    print()

    print("--- 参数格式错误（order_id 不符合正则）---")
    try:
        await agent.call("refund", order_id="ABC-123", reason="质量问题")
    except ValueError as e:
        print("拦截:", e)


asyncio.run(main())