# 我们需要一个 **依赖注入函数** 来提供数据库会话。


# 告诉 Python：Session 是什么类型
from sqlalchemy.orm import Session

# ✅ SessionLocal 是你在 database/connection.py 里用 sessionmaker() 创建的，它不是 session 本身，而是一个能生成 session 的“工厂”。
from database.connection import SessionLocal


def get_db_session() -> Session:
    """
    数据库会话依赖项。
    每次请求时创建一个新会话，请求结束后自动关闭。
    """
    # 调用“会话工厂” SessionLocal()，真正创建一个数据库会话实例，
    # 此时，它已经连接到你的 library.db 数据库了！
    session = SessionLocal()

    # FastAPI 自动处理 yield 的生命周期，你完全不用操心关闭连接
    # 用 yield 实现“请求期间保持连接，结束后自动关闭”
    try:
        yield session # 把 session 交给路由函数使用
    finally:
        session.close()  # 无论成功/异常，都会执行关闭！

# ✅ 关键点：

# - `yield` 是生成器语法，FastAPI 会在请求处理完后**自动执行 `finally` 块**
# - 这样就**不需要手动写 `db.close()`**，避免连接泄漏！


# 总结：
# （1）✅ 用 yield（生成器 + 上下文管理）：
# FastAPI 看到你的依赖函数里有 yield，就会这样处理：

# 请求到来时：
# 执行到 yield session
# 把 session 传给你的路由函数
# 暂停这个函数（但不结束！）
# 你的路由函数执行完后（比如返回了 JSON）：
# FastAPI 自动回到这个函数
# 继续执行 finally 块
# 调用 session.close() → 安全关闭数据库连接
# 🧠 你可以把 yield 想象成：“先借给你用，用完我再回来收尾”


# （2）每次请求时：
# 打开一个数据库连接（session）
# 用完后自动关闭它（避免连接泄漏）
# 这就是 get_db_session() 的作用！


# 🧠 为什么用 `yield` 而不是 `return`？
# | 方式                    | 是否自动关闭？ | 能否处理异常？ | 推荐？ |
# | ----------------------- | -------------- | -------------- | ------ |
# | `return SessionLocal()` | ❌ 不会关闭     | ❌ 可能泄漏     | 否     |
# | 手动 `db.close()`       | ✅ 但容易忘     | ❌ 忘记就泄漏   | 否     |
# | **`yield` + `finally`** | ✅ 自动关闭     | ✅ 即使出错也关 | ✅ 是   |
# FastAPI 的依赖注入系统会**自动处理生成器的生命周期**，yield 的用法这是官方推荐做法。

