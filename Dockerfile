# 베이스 이미지 설정
FROM python:3.10-slim

# 필요한 패키지 설치
RUN apt-get update && \
    apt-get install -y wget unzip curl \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libappindicator3-1 \
    libx11-xcb1 \
    libxcomposite1 \
    libasound2 \
    libatk1.0-0 \
    libcups2 \
    libgtk-3-0 \
    libdbus-glib-1-2 && \
    rm -rf /var/lib/apt/lists/*

# 최신 Chromium 다운로드 및 설치
RUN wget -O /tmp/chrome-linux64.zip "https://storage.googleapis.com/chrome-for-testing-public/114.0.5735.90/linux64/chrome-linux64.zip" && \
    unzip /tmp/chrome-linux64.zip -d /usr/local/chrome && \
    chmod +x /usr/local/chrome/chrome-linux64/chrome && \
    ln -s /usr/local/chrome/chrome-linux64/chrome /usr/bin/chromium-browser && \
    rm /tmp/chrome-linux64.zip

# 최신 ChromeDriver 다운로드 및 설치
RUN wget -O /tmp/chromedriver-linux64.zip "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver-linux64.zip -d /usr/local/chromedriver && \
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
