from celery import Celery

# 创建 Celery 对象
celery_app = Celery(
    "python-fast-api",
    broker="redis://localhost:6379/0",  # Broker：任务队列
    backend="redis://localhost:6379/0",   # Backend：存储任务结果
    include=["tasks.tasks"] #通过 `include` 参数自动导入异步任务
)

# - **`"python-fast-api"`**：这是你给这个 Celery 应用起的名字，你可以换成你自己的项目名。
# - **`broker="redis://localhost:6379/0"`**：这指定了任务队列（消息中间件）的地址。`redis://` 表示我们用的是 Redis；`localhost` 表示 Redis 服务在本地电脑上运行；`6379` 是 Redis 的默认端口号；`/0` 表示使用 Redis 的第 0 个数据库。
# - **`backend="redis://localhost:6379/0"`**：这指定了任务执行结果的存储地址。这里和 `broker` 用了同一个 Redis 地址和数据库，对于开发和测试来说是完全可以的。

# 可选：配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True   # 开启 STARTED 状态
)

# - **`task_serializer="json"`**：设置任务的序列化方式为 JSON。简单说，就是任务的数据会用 JSON 格式来打包和传输，这是一种通用且安全的方式。
# - **`accept_content=`**：告诉 Celery 只接受 JSON 格式的内容。
# - **`result_serializer="json"`**：设置任务结果的序列化方式也为 JSON。
# - **`timezone="Asia/Shanghai"`**：设置时区为上海（也就是北京时间），这样任务的时间戳会更符合你的习惯。
# - **`enable_utc=False`**：禁用 UTC 时间，配合上面的时区设置。

# 配置日志
celery_app.conf.worker_loglevel = "INFO"
celery_app.conf.worker_pool = "solo"