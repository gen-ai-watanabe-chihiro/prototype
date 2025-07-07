# -------------------------------------------------
# ・ファイル名：Dockerfile
# ・ファイル内容：フロントエンド用Dockerファイル
# ・作成日時：2025/07/06 17:56:00  Claude Code
# -------------------------------------------------

FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]