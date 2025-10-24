from core.celery_app import celery_app


@celery_app.task
def add(x, y):
    return x + y

if __name__ == "__main__":
    result = add.delay(4,6)
    print("Task ID:", result.id)
    print("Result:", result.get(timeout=10))  # 阻塞等待结果
     

