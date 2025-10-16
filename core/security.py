from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status
from core.exceptions import UnauthorizedException

import os
from dotenv import load_dotenv
load_dotenv()
# 创建密码工具函数
# 声明使用 argon2 算法
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
# 验证密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码是否与哈希匹配"""
    return pwd_context.verify(plain_password, hashed_password)
# 对密码进行哈希
def get_password_hash(password: str) -> str:
    """对明文密码进行哈希"""
    return pwd_context.hash(password)


# 创建 JWT 工具函数
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
#  `create_access_token({"sub": "alice"})` → 返回一串 JWT 字符串

        
# 添加 JWT 解码函数
def decode_access_token(token: str) -> str:
    """解码 JWT，返回 username（即 'sub' 字段）"""
    try:
        payload = jwt.decode(token=token,key=SECRET_KEY,algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise UnauthorizedException("无法验证凭据")
        return username
    except JWTError:
        raise UnauthorizedException("无法验证凭据")




# if __name__ == "__main__":
#     # 测试
#     # 假设明文密码是 '123456'
#     hashed_password = get_password_hash("123456")
#     print(hashed_password) # $argon2id$v=19$m=65536,t=3,p=4$cY4x5jxHqLW21tp7711rjQ$BpDTE0fnvlsNbf0dEWpnie4pkV4e2o1+Ms+e2k7ERqE
#     print(verify_password("123456", hashed_password))