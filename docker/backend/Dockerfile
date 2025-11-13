# Library RAG Agent - 後端 Dockerfile
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安裝系統依賴
# - build-essential: 編譯 Python 套件所需
# - libmysqlclient-dev: MySQL 客戶端函式庫
# - pkg-config: 編譯工具
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 複製應用程式碼 (開發時會被 volume 掛載覆蓋)
COPY . .

# 創建必要的目錄
RUN mkdir -p /app/storage/documents /app/storage/chroma_db

# 暴露端口
EXPOSE 8000

# 啟動命令 (會被 docker-compose.yml 覆蓋)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
