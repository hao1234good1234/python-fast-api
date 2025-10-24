# 新建文件，放工具函数
import json
from datetime import datetime, timezone
from infrastructure.models import AuditLog
from infrastructure.connection import SessionLocal

# 异步任务函数，将日志写入文件
# ✅ 这个函数是 **独立的、无状态的**，非常适合做后台任务。
# log_borrow_event` 是在 **当前进程的子线程** 中执行的，所以：
# - 不要传 `db` 会话（会话不能跨线程）
# - 如果要写数据库，需在函数内部新建会话
def log_borrow_event(user_id: str, book_id: str, borrow_id: int):
    """后台任务：记录借书日志（写入文件）"""
    log_entry = {
        "event": "borrow_created",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "book_id": book_id,
        "borrow_id": borrow_id,
        "status": "success"
    }
    # 写入日志到文件（追加模式）
    with open("data/borrow_events.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    # 控制台输出日志
    print(f"[Background] Logged borrow event: user={user_id}, book={book_id}")

# 异步任务函数，将日志写入数据库audit_logs 表
def log_borrow_to_db(user_id: str, book_id: str, borrow_id: int):
    """
    后台任务：将借书事件写入 audit_logs 表
    """
    db = SessionLocal()
    try:
        log_entry = AuditLog(
            action="borrow_created",
            user_id= user_id,
            details = {
                "book_id": book_id,
                "borrow_id": borrow_id,
                "event": "user borrowed a book"
            }
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        # 可选：记录错误日志（不要让后台任务崩溃主请求）
        print(f"[ERROR] failed to log to db: {e}")
        db.rollback()
    finally:
        db.close()

