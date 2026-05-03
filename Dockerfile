FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製檔案
COPY . .

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# Cloud Run 用 gunicorn 啟動（比 flask run 穩）
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "kktixW:app"]