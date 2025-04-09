# 開発用ステージ
FROM python:3.11-slim

WORKDIR /app

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# セキュリティのための非rootユーザー作成
RUN useradd -m -u 1000 appuser

# 依存関係のインストール
COPY requirements.txt .
RUN pip install -r requirements.txt

# 所有権の変更
RUN chown -R appuser:appuser /app

# 非rootユーザーに切り替え
USER appuser

# 環境変数の設定
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# アプリケーションの起動（開発モード）
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"] 