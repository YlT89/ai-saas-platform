# 1. 基础镜像：使用官方轻量级的 Python 3.11 版本
FROM python:3.11-slim

# 2. 设置环境变量：让 Python 直接输出日志到控制台（不缓冲），且不生成 .pyc 文件
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. 设置工作目录（容器内部的路径）
WORKDIR /app

# 4. 先拷贝依赖清单，并安装依赖
# 这样做的好处是：如果你只改了代码没改依赖，Docker 会自动使用缓存，不用重新下载依赖，极快！
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 拷贝项目里的所有代码到容器中
COPY . .

# 6. 暴露端口：告诉 Docker 这个容器运行在 8000 端口
EXPOSE 8000

# 7. 启动命令：当容器启动时，执行 uvicorn 启动服务
CMD ["uvicorn", "main9:app", "--host", "0.0.0.0", "--port", "8000"]