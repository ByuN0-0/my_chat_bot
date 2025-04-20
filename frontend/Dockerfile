# Node.js LTS 버전을 기반 이미지로 사용
FROM node:lts-alpine

# 작업 디렉토리 설정
WORKDIR /app

# package.json과 lock 파일 먼저 복사 (의존성 캐싱 활용)
# package-lock.json 또는 yarn.lock 파일이 있다면 함께 복사됩니다.
COPY package*.json ./

# 의존성 설치
# CI=true 환경 변수는 경고를 오류로 취급하지 않도록 하고,
# 불필요한 사용자 인터랙션 프롬프트를 방지합니다.
ENV CI=true
RUN npm install
# 또는 yarn 사용 시: RUN yarn install --frozen-lockfile

# 나머지 소스 코드 복사
COPY . .

# Vite 개발 서버 포트 노출
EXPOSE 5173

# 개발 서버 실행 (외부 접근 가능하도록 --host 플래그 추가)
CMD ["npm", "run", "dev", "--", "--host"]