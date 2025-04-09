# 開発用ステージ
FROM node:18-slim

WORKDIR /app

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 所有権の変更 (nodeユーザーに変更)
RUN chown -R node:node /app

# node ユーザーに切り替え
USER node

# 環境変数の設定
ENV PORT=3000
ENV NODE_ENV=development

# Next.jsアプリケーションの起動
CMD ["npm", "run", "dev"]
