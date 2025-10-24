from pydantic_settings import BaseSettings
from typing import Literal

#.env的优先级比settings.py高
class Settings(BaseSettings):
    # 环境
    APP_ENV: Literal["development", "production", "testing"] = "development"

    # 数据库
    DATABASE_URL: str

    #JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 邮件
    EMAIL_163_FROM: str # 默认用环境变量中的发件人邮箱，一般是公司邮箱
    EMAIL_163_PASSWORD: str # 默认用环境变量中的授权码

    # 其他
    API_V1_STR: str = "/api/v1"
    # Config这是 Pydantic 的**内部配置类**
    # 注意：在 Pydantic v2 中，`Config` 类的方式**已被弃用**，推荐使用 **`model_config` 字典**。
    model_config = {
        "env_file": ".env",  # ✅ 默认加载 .env，修改成生产环境只需要修改为 .env.prod
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # 忽略 .env 中未定义的变量
    }
    # 旧版本用法
    # class Config:
    #     env_file = ".env"  # 默认加载 .env
    #     env_file_encoding = "utf-8"
    @property
    def is_dev(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_prod(self) -> bool:
        return self.APP_ENV == "production"

# 单例
settings = Settings()