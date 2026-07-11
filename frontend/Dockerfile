FROM node:20-slim

WORKDIR /app

# 複製 package 檔案並安裝 dependencies
COPY package*.json ./
RUN npm install

# 複製專案原始碼
COPY . .

EXPOSE 3000

# 預設啟動 Next.js 開發伺服器以方便與本地後端 API 即時互動
CMD ["npm", "run", "dev"]
