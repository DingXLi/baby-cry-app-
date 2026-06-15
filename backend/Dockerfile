FROM node:20-alpine AS base
WORKDIR /app

# 只复制依赖定义，利用 Docker 层缓存
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# 复制应用代码
COPY src ./src

# 创建上传目录
RUN mkdir -p uploads && chown -R node:node /app

USER node
EXPOSE 3000

ENV NODE_ENV=production

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

CMD ["node", "src/index.js"]
