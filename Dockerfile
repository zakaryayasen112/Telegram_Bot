# 🐳 Dockerfile بۆ هۆستینگی ٢٤/٧
FROM python:3.11-slim

# FFmpeg دامەزراندن (پێویستە بۆ MP3)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# پێویستیەکان دامەزراندن
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کۆدی بۆت کۆپیکردن
COPY telegram_bot.py .

# دروستکردنی فۆڵدەری داونلۆد
RUN mkdir -p downloads

CMD ["python", "telegram_bot.py"]
