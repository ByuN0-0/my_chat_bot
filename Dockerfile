# Python 3.10 슬림 버전을 기반 이미지로 사용
FROM python:3.10-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 프로젝트 코드 전체 복사
COPY . .

# uvicorn 실행 명령은 docker-compose.yml에서 정의하므로 여기서는 생략 가능
# 기본 포트 노출 (문서화 목적)
# EXPOSE 8000

# 기본 실행 명령 (docker-compose.yml의 command로 덮어쓰여짐)
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]