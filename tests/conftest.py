import pytest
from settings import Settings

@pytest.fixture(autouse=True)
def override_settings():
    # 强制测试环境使用内存数据库
    Settings.model_config['env_file'] = None  # 不加载 .env
    settings = Settings(
        APP_ENV="testing",
        DATABASE_URL="sqlite:///:memory:",
        SECRET_KEY="test-secret",
        ACCESS_TOKEN_EXPIRE_MINUTES=5
    )
    # 替换全局 settings（需小心）
    import sys
    sys.modules['settings'].settings = settings