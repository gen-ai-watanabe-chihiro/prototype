# -------------------------------------------------
# ・ファイル名：Dockerfile
# ・ファイル内容：バックエンド用Dockerファイル
# ・作成日時：2025/07/06 17:56:00  Claude Code
# -------------------------------------------------

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]