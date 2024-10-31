# 베이스 이미지 설정
FROM python:3.10-slim

# 필요한 패키지 설치
RUN apt-get update && \
    apt-get install -y wget unzip curl && \
    rm -rf /var/lib/apt/lists/*

# 최신 Chromium 다운로드 및 설치
RUN wget -O /tmp/chrome-linux64.zip "https://storage.googleapis.com/chrome-for-testing-public/130.0.6723.91/linux64/chrome-linux64.zip" || { echo "Failed to download Chrome"; cat /tmp/chrome-linux64.zip; exit 1; } && \
    unzip /tmp/chrome-linux64.zip -d /usr/local/chrome || { echo "Failed to unzip Chrome"; exit 1; } && \
    chmod +x /usr/local/chrome/chrome && \
    ln -s /usr/local/chrome/chrome /usr/bin/chromium-browser && \
    rm /tmp/chrome-linux64.zip

# 최신 ChromeDriver 다운로드 및 설치
RUN wget -O /tmp/chromedriver-linux64.zip "https://storage.googleapis.com/chrome-for-testing-public/130.0.6723.91/linux64/chromedriver-linux64.zip" || { echo "Failed to download ChromeDriver"; cat /tmp/chromedriver-linux64.zip; exit 1; } && \
    unzip /tmp/chromedriver-linux64.zip -d /usr/local/chromedriver || { echo "Failed to unzip ChromeDriver"; exit 1; } && \
    chmod +x /usr/local/chromedriver/chromedriver && \
    ln -s /usr/local/chromedriver/chromedriver /usr/bin/chromedriver && \
    rm /tmp/chromedriver-linux64.zip

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 프로젝트 파일 복사
COPY . .

# 포트 설정
EXPOSE 8000

# Django 앱 시작 명령어 설정
CMD ["gunicorn", "django_performance_tool.wsgi:application", "--bind", "0.0.0.0:8000"]
