import os
import uvicorn
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# 라우터 임포트
from routes.chat import router as chat_router
from routes.admin import router as admin_router
# MongoDB 연결/종료 함수 임포트
from db.mongo import connect_to_mongo, close_mongo_connection

# 로깅 설정
log_file = "app.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# Startup 이벤트 핸들러: 앱 시작 시 MongoDB 연결
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

# Shutdown 이벤트 핸들러: 앱 종료 시 MongoDB 연결 종료
@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# templates와 static 폴더 생성 확인 및 설정
if not os.path.exists("templates"):
    os.makedirs("templates")
    logger.info("templates 폴더 생성됨")
if not os.path.exists("static"):
    os.makedirs("static")
    logger.info("static 폴더 생성됨")

app.mount("/static", StaticFiles(directory="static"), name="static")

# 라우터 등록
app.include_router(chat_router)
app.include_router(admin_router)

if __name__ == "__main__":
    logger.info("애플리케이션 시작 (단독 실행 모드)")
    # uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
    uvicorn.run(app, host="127.0.0.1", port=8000) # Docker Compose에서 실행 시 이 부분은 사용되지 않음