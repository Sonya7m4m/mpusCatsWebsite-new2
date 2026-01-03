# 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt 

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 暴露端口（和服务端口一致）
EXPOSE 80

# 启动命令
CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
