@echo off
:: 启动 Celery Worker 脚本
:: 双击运行即可启动，按 Ctrl+C 停止
echo 启动 Celery Worker...
cd /d E:\Projects\vscode\python-fast-api
call venv\Scripts\activate

:: 日志存放在项目根目录下logs文件夹下
if not exist logs mkdir logs
:: 编码格式改为utf-8
chcp 65001 >nul

:: 启动 Celery Worker，使用 solo pool（Windows 必须），将日志记录到文件中
:: E:\Projects\vscode\python-fast-api\venv\Scripts\python.exe -m celery -A core.celery_app worker --loglevel=info --pool=solo -c 4 >> logs/celery-worker.log 2>&1

python -m celery -A core.celery_app worker --loglevel=info --pool=solo -c 4

echo Celery Worker 已停止。
pause