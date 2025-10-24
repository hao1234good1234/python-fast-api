from starlette.middleware.base import BaseHTTPMiddleware
# ✅ SessionLocal 是你在 database/connection.py 里用 sessionmaker() 创建的，它不是 session 本身，而是一个能生成 session 的“工厂”。
from infrastructure.connection import SessionLocal
class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # 调用“会话工厂” SessionLocal()，真正创建一个数据库会话实例，
        # 此时，它已经连接到你的 library.db 数据库了！
        db = SessionLocal()
        request.state.db = db
        try:
            response = await call_next(request)
            db.commit()
            return response
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


