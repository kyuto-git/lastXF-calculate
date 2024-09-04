# ベースイメージとしてPython 3.9を使用
FROM python:3.9-slim

# 作業ディレクトリを作成
WORKDIR /app

# 必要なPythonパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコンテナにコピー
COPY . .

# メインスクリプトを実行
CMD ["python", "process_csv.py"]
