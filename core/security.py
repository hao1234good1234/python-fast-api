# 创建密码工具函数
from passlib.context import CryptContext

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

# if __name__ == "__main__":
#     # 测试
#     # 假设明文密码是 '123456'
#     hashed_password = get_password_hash("123456")
#     print(hashed_password) # $argon2id$v=19$m=65536,t=3,p=4$cY4x5jxHqLW21tp7711rjQ$BpDTE0fnvlsNbf0dEWpnie4pkV4e2o1+Ms+e2k7ERqE
#     print(verify_password("123456", hashed_password))