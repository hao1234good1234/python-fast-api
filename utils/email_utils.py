import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.logger import get_logger
from settings import settings

logger = get_logger(__name__)
import time

# 发送邮件
def send_email(
        to_email: str,
        subject: str,
        body: str,
        from_email: str = "noreply@yourapp.com",
        smtp_host: str = "smtp.example.com",
        smtp_port: int = 587,
        smtp_user: str = "your_user",
        smtp_password: str = "your_password"
):
    """
    同步发送邮件函数 —— 用于 BackgroundTasks
    注意：这是一个阻塞 I/O 操作，但 FastAPI 会在线程池中运行它，不阻塞主线程
    """
    try:
        # 创建邮件对象
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # 连接SMTP服务器：（示例：163邮箱）
        with smtplib.SMTP(smtp_host,smtp_port) as server:
            server.starttls() # 启用 TLS 加密
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        logger.info(f"Email sent to {to_email}")
        print(f"Email sent to {to_email}: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        print(f"Failed to send email to {to_email}: {e}")
        # 注意：后台任务异常不会影响主请求，但要自己处理错误


# 发送163邮箱测试邮件
def send_email_163(
        to_email: str, # 收件人
        subject: str,
        body: str,
        from_email: str = None,  # 默认用环境变量中的 发件人
        smtp_password: str = None # 默认用环境变量中的 授权码
):
    """
    使用 163 邮箱 SMTP 发送邮件（同步函数，适用于 FastAPI BackgroundTasks）
    同步发送邮件 —— 会被 FastAPI 在线程池中执行
    """
    # time.sleep(5)  # 模拟发邮件耗时 5 秒
    from_email = from_email or settings.EMAIL_163_FROM
    smtp_password = smtp_password or settings.EMAIL_163_PASSWORD

    if not from_email or not smtp_password:
        raise ValueError("请设置环境变量 EMAIL_163_FROM 和 EMAIL_163_PASSWORD")
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # 连接163 SMTP服务器
        with smtplib.SMTP("smtp.163.com", 25) as server:
            # 163 的 SMTP 端口：25（明文）或 465（SSL），但 25 更稳定
            # 注意：有些网络会屏蔽 25 端口，可尝试 465 + SMTP_SSL（见下方备注）
            server.login(from_email, smtp_password)
            server.send_message(msg)

        logger.info(f"邮件已经发送到 {to_email}")
        print(f"邮件已经发送到{to_email}: {subject}")
    except Exception as e:
        logger.error(f"邮件发送失败 {to_email}: {e}")
        print(f"邮件发送失败 {to_email}: {e}")
        raise  # 可选：是否让后台任务抛出异常