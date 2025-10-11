# 学习python的fast api的项目代码
# 📚 图书管理系统

一个基于 Python + FastAPI 的图书管理服务，支持借阅、归还、持久化和 REST API。

## ✨ 功能
- 添加图书
- 借书 / 还书
- 查看用户借阅列表
- JSON 持久化
- 自动生成 API 文档

## 🚀 快速启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务
uvicorn api.main:app --reload

# 3. 访问文档
http://127.0.0.1:8000/docs