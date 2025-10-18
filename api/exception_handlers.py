# 如果你有很多自定义异常，可以注册 **全局异常处理器**，避免每个路由都写 `try-except`：

# ```python
# # api/main.py or api/exception_handlers.py
# from fastapi import FastAPI
# from core.exceptions import BorrowRecordNotFound, BorrowPermissionDenied

# app = FastAPI()

# @app.exception_handler(BorrowRecordNotFound)
# async def borrow_not_found_handler(request, exc):
#     return JSONResponse(
#         status_code=404,
#         content={"detail": "借阅记录不存在"}
#     )

# @app.exception_handler(BorrowPermissionDenied)
# async def permission_denied_handler(request, exc):
#     return JSONResponse(
#         status_code=403,
#         content={"detail": "无权操作他人的借阅记录"}
#     )
# ```

# 然后 API 层代码更简洁：

# ```python
# @router.patch("/{borrow_id}/return")
# def return_book(...):
#     result = service.return_book(borrow_id, current_user.user_id)  # 无需 try-except！
#     db.commit()
#     return result
# ```

# > ✅ 异常自动被全局处理器转为 HTTP 响应，同时保持事务回滚（需配合中间件或依赖注入处理 db.rollback）。