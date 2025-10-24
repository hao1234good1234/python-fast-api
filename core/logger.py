import logging
import sys
import json
from datetime import datetime, timezone
from pythonjsonlogger import jsonlogger # pip install python-json-logger
from settings import settings # 从 settings.py 中导入设置

# 自定义 JSON 格式化器
# 需要根据不同环境选择不同的日志格式
# 环境修改 settings.py
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    自定义 JSON 格式化器
    """
    def add_fields(self, log_dict, record, message_dict):
        super().add_fields(log_dict, record, message_dict)
        if not log_dict.get('timestamp'):
            # 使用 ISO 8601 格式时间戳
            log_dict['timestamp'] =  datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        if log_dict.get('level'):
            log_dict['level'] = log_dict['level'].upper()
        else:
            log_dict['level'] = record.levelname
        # 添加环境信息
        log_dict['env'] = settings.APP_ENV

def get_logger(name: str) -> logging.Logger:
    """获取配置好的logger实例"""
    logger = logging.getLogger(name)
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG if settings.is_dev else logging.INFO)  # 设置日志级别

    if settings.is_prod:
        # 生产环境输出json
        handler = logging.StreamHandler(sys.stdout)
        formatter = CustomJsonFormatter(
                '%(timestamp)s %(level)s %(name)s %(message)s %(event)s',
                json_ensure_ascii=False, # 关键！防止中文转义
                json_indent=2 # 缩进2个空格
        )
        handler.setFormatter(formatter)
    else:
        # 开发环境输出彩色易读文字
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(levelname)-8s %(asctime)s — %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

    logger.addHandler(handler) # **handler** = “日志要输出到哪里”（屏幕、文件、网络等）  
    logger.propagate = False  #  防止日志被上级重复打印
    return logger
       
# 这个 logger 会：
# - 自动根据 `APP_ENV` 切换格式
# - 添加 `timestamp`、`env` 等字段
# - 支持传入结构化数据（如 `user_id`, `book_id`）

