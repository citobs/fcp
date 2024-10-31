# 베이스 이미지로 Python 3.9 사용
FROM python:3.9-slim

# 시스템 패키지 업데이트 및 Chrome 설치
RUN apt-get update && \
    apt-get install -y wget gnupg && \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# ChromeDriver 설치
RUN wget -O /usr/local/bin/chromedriver https://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip && \
    chmod +x /usr/local/bin/chromedriver

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 복사 후 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 파일 복사
COPY . .

# 환경변수 설정 (Render가 기본 포트로 사용)
ENV PORT 8000
EXPOSE $PORT

# Django의 Gunicorn 웹 서버 설정
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "django_performance_tool.wsgi:application"]
