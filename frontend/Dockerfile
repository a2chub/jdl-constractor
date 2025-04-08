# ビルドステージ
FROM node:18-slim as builder

WORKDIR /app

# 依存関係のインストール
COPY package*.json ./
RUN npm ci

# ソースコードのコピーとビルド
COPY . .
RUN npm run build

# 実行ステージ
FROM node:18-slim

WORKDIR /app

# セキュリティのため非root userを作成
RUN useradd -m -u 1000 appuser

# ビルド成果物と必要なファイルのコピー
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/node_modules ./node_modules

# 所有権の変更
RUN chown -R appuser:appuser /app

# 非root userに切り替え
USER appuser

# 環境変数の設定
ENV PORT=3000
ENV NODE_ENV=production

# アプリケーションの起動
CMD ["npm", "start"] 