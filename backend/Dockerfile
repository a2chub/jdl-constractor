# ビルドステージ
FROM python:3.11-slim as builder

WORKDIR /app

# 必要なパッケージのインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# 依存関係のインストール
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# 実行ステージ
FROM python:3.11-slim

# セキュリティのため非root userを作成
RUN useradd -m -u 1000 appuser

WORKDIR /app

# ビルドステージから必要なファイルをコピー
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# 依存関係のインストール
RUN pip install --no-cache /wheels/*

# アプリケーションのコピー
COPY ./app ./app

# 所有権の変更
RUN chown -R appuser:appuser /app

# 非root userに切り替え
USER appuser

# 環境変数の設定
ENV PORT=8000

# アプリケーションの起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 