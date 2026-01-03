# 使用官方 Python 镜像
FROM python:3.9-slim
# 设置工作目录
WORKDIR /app
# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# 复制项目代码
COPY . .
# 暴露端口（CloudBase Run 默认监听8080）
EXPOSE 8080
# 使用 Gunicorn 启动应用
CMD ["gunicorn", "-b", "0.0.0.0:8080", "你的应用模块名:app"]
