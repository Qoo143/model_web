# Library RAG Agent - 前端 Dockerfile
FROM node:20-alpine

# 設定工作目錄
WORKDIR /app

# 複製 package.json 和 package-lock.json
COPY package*.json ./

# 安裝依賴
RUN npm install

# 複製應用程式碼 (開發時會被 volume 掛載覆蓋)
COPY . .

# 暴露 Vite 開發伺服器端口
EXPOSE 5173

# 啟動命令 (會被 docker-compose.yml 覆蓋)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
