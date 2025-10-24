# 异步任务路由
from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from core.celery_app import celery_app
from api.schemas import TaskResponse

router = APIRouter()
# 创建异步任务路由
@router.get("/task_status/{task_id}", summary="根据任务ID查询任务状态")
async def get_task_status(task_id: str):
    """
    查询 Celery 任务的执行状态和结果
    状态可能为：
    - PENDING: 任务还未开始（可能在队列中）
    - STARTED: 任务已开始执行
    - SUCCESS: 任务成功完成
    - FAILURE: 任务执行失败
    - RETRY: 任务正在重试
    - REVOKED: 任务被取消
    """
    # 使用 AsyncResult 查询任务状态
    try:
        # 创建 AsyncResult 对象
        result = AsyncResult(task_id, app=celery_app)
        # final_result = result.get(timeout=10)  # 最多等10秒
        # 构建基础响应
        response = TaskResponse(task_id=task_id, state=result.state, ready=result.ready())

        # 如果任务已完成
        if result.ready():
            if result.successful():
                response.to_response()["result"] = result.result
            elif result.failed():
                # 失败时 result 是异常对象
                response.to_response()["error"] = str(result.result)
                response.to_response()["traceback"] = result.traceback  # 可选：返回堆栈
        else:
            # 任务未完成
            if result.state == "STARTED" and hasattr(result, "info"):
                # 可附加执行信息，如 PID
                response.to_response()["pid"] = getattr(result.info, "pid", None)

        return response.to_response()

    except Exception:
        # 防止内部错误暴露给前端
        raise HTTPException(status_code=500, detail="查询任务状态时发生内部错误")

# | 方法/属性       | 说明                                           | 返回值               |
# | --------------- | ---------------------------------------------- | -------------------- |
# | `.id`           | 任务的 UUID                                    | `str`                |
# | `.state`        | 当前状态（`PENDING`, `SUCCESS`, `FAILURE` 等） | `str`                |
# | `.ready()`      | 任务是否完成（成功或失败）                     | `bool`               |
# | `.result`       | 任务结果（成功时为返回值，失败时为异常）       | `Any` 或 `Exception` |
# | `.successful()` | 任务是否成功完成                               | `bool`               |
# | `.failed()`     | 任务是否失败                                   | `bool`               |
# | `.traceback`    | 失败时的完整堆栈信息                           | `str`                |