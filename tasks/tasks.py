from celery import Celery, shared_task
from core.celery_app import celery_app
import time
from utils.email_utils import send_email_163
from core.logger import get_logger
import random

logger = get_logger(__name__)

# `@celery_app.task`：这是一个装饰器，告诉 Celery：“这个函数是一个异步任务”。
# `bind=True`：表示这个任务可以访问 `self` 对象（例如获取任务 ID、状态等），不是必须的，但推荐用于调试。
# 函数参数：和普通函数一样，支持类型提示（`str`, `int` 等）。
# 返回值：会被存入结果后端（Redis），可以通过 `task_id` 查询结果。

# 模拟发送欢迎邮件的异步任务
@celery_app.task(bind=True)
@shared_task(
    autoretry_for=(Exception,),       # 哪些异常触发重试
    retry_kwargs={"max_retries": 3},  # 最多重试 3 次
    retry_backoff=10,           # 每次重试间隔 10 秒（指数退避）
    retry_jitter=True,   # 添加随机抖动，避免雪崩
    bind=True      # 必须加 bind=True 才能访问 self
)
def send_email_task(self, to_email: str, subject: str, body: str):
    """
    模拟发送邮件的异步任务
    """
    task_id = send_email_task.request.id
    # 重试次数
     # 获取当前是第几次执行（0 表示第一次，1 表示第一次重试，以此类推）
    retry_count = self.request.retries
    attempt = retry_count + 1  # 当前尝试次数（从 1 开始）
    max_retries = 3
    if retry_count == 0:
        logger.info(f"[任务 {task_id}] [尝试 {attempt}/{max_retries}] 正在发送邮件给 {to_email}")
    else:
        logger.warning(f"[任务 {task_id}] [重试 {retry_count}/{max_retries}] 正在重试发送邮件给 {to_email}")

    # 模拟随机失败（用于测试重试）
    # if random.random() < 0.8:
    #     logger.warning(f"[任务 {task_id}] [尝试 {attempt}/{max_retries}] 邮件发送失败，准备重试...")
    #     raise Exception("网络超时")

    # 这里可以调用真实的邮件服务，比如 SMTP 或第三方 API
    send_email_163(to_email=to_email, subject=subject, body=body)
    
    print(f"借书邮件已经发送到 {to_email}")
    logger.info(f"借书邮件已经发送到 {to_email}")
    return f"借书邮件已经发送到 {to_email}"
