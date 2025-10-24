import time
from fastapi import Request
from core.logger import get_logger

logger = get_logger("api")  #创建一个专门叫 `"api"` 的日志记录器,这样日志里会显示 `name: "api"`，知道是接口日志，不是业务日志

# 定义一个**异步函数**（因为 FastAPI 是异步的）
# `request`：用户的请求对象（包含 URL、方法、headers 等）
# `call_next`：**一个函数**，调用它就会继续执行后面的代码（比如你的 `@app.get("/books")`）
# `call_next(request)` = “把请求交给下一个环节（你的业务代码）处理”
async def logging_middleware(request: Request, call_next):
    start_time = time.time() # 记录请求开始时间
    # - ⏳ **等待业务代码执行完**
    # - 比如用户访问 `/borrow`，这里会等 `borrow_book()` 函数跑完
    # - `response` 是业务代码返回的结果（比如 JSON 数据、404 错误等）
    response = await call_next(request)
    process_time = time.time() - start_time # 计算请求处理时间


    # 记录一条结构化日志！
    # `extra` 里的每个字段都会变成 JSON 的一个 key
    logger.info(
        "请求处理完成", # 日志标题
        extra={
            "event": "HTTP_REQUEST",
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": round(process_time, 3)

        }
    )
    # 把业务代码的返回结果**原样返回给用户**
    # 中间件不能“吃掉”响应！
    return response