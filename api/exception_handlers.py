# 全局异常处理器（FastAPI）
# 如果你有很多自定义异常，可以注册 **全局异常处理器**，避免每个路由都写 `try-except`：

from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from core.exceptions import BusinessException
import logging

logger = logging.getLogger(__name__)

# - 这是一个**普通函数**，接收一个 `FastAPI` 实例（`app`），目的是**把异常处理器“注册”到 app 上**
def register_exception_handlers(app: FastAPI):

    # 注册 BusinessException 处理器
    # 这是 **装饰器（Decorator）** 语法
    # `@app.exception_handler(...)` 的作用是：**“当程序抛出 `BusinessException` 时，请调用下面这个函数来处理”**
    @app.exception_handler(BusinessException)

    # `exc: BusinessException`：**被捕获到的异常实例**（就是你 `raise BookNotAvailableError(...)` 那个对象）
    async def business_exception_handler(request: Request, exc: BusinessException):
        logger.warning(f"业务异常: {exc.code} | {exc.detail}")
        return JSONResponse(
            status_code=400,  # 业务错误用400
            content={
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
                "path": request.url.path
            }
        )
    # 兜底异常处理器（捕获所有未处理异常）
    #     - 如果代码抛出了**未预料的异常**（比如数据库连接失败、空指针等）
    # - 我们不想让用户看到 FastAPI 默认的 **500 错误页面（含堆栈信息）**
    # - 而是返回一个**友好的错误提示**，同时**记录详细日志**
    @app.exception_handler(Exception)
    async def unexpected_exception_handler(request: Request, exc: Exception):
        logger.error(f"未知异常: {exc}", exc_info=True) #日志会**自动包含完整的异常堆栈跟踪（Traceback）**
        return JSONResponse(
            status_code=500,  # 服务器错误用500
            content={
                "code": "INTERNAL_ERROR",
                "message": "服务器内部错误",
                "detail": None,
                "path": request.url.path
            }
        )