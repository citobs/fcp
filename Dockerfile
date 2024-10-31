# 베이스 이미지 설정
FROM python:3.10-slim

# 필요한 패키지 설치
RUN apt-get update && \
    apt-get install -y wget unzip curl chromium && \
    rm -rf /var/lib/apt/lists/*

# ChromeDriver 다운로드 및 설치
RUN wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 프로젝트 파일 복사
COPY . .

# 포트 설정 (Render 또는 다른 서비스에 맞게 변경)
EXPOSE 8000

# Django 앱 시작 명령어 설정
CMD ["gunicorn", "django_performance_tool.wsgi:application", "--bind", "0.0.0.0:8000"]
