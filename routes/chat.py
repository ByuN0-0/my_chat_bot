import logging
from fastapi import APIRouter, HTTPException, Request # Request 추가
from fastapi.responses import HTMLResponse # HTMLResponse 추가
from fastapi.templating import Jinja2Templates # Jinja2Templates 추가

from schemas.chat import UserMessage
from services.openai_service import get_chat_response
from db.mongo import save_chat_message, get_chat_history, get_all_sessions # get_all_sessions 추가

logger = logging.getLogger(__name__)
router = APIRouter()

# templates 설정 (app.py와 동일하게 설정)
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    logger.info("루트 페이지 요청 받음 (라우터)")
    return templates.TemplateResponse("index.html", {"request": request})

# 새로운 엔드포인트: 모든 세션 ID 목록 조회
@router.get("/sessions")
async def get_sessions():
    logger.info("세션 목록 요청 받음")
    try:
        session_ids = await get_all_sessions()
        return {"sessions": session_ids}
    except Exception as e:
        logger.error(f"세션 목록 조회 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="세션 목록 조회 중 오류가 발생했습니다.")

# 새로운 엔드포인트: 대화 기록 조회
@router.get("/history/{conversation_id}")
async def get_history(conversation_id: str):
    logger.info(f"대화 기록 요청 받음: ConvID={conversation_id}")
    if not conversation_id:
        raise HTTPException(status_code=400, detail="conversation_id가 필요합니다.")

    try:
        history = await get_chat_history(conversation_id) # db/mongo.py의 함수 사용
        return history # 조회된 기록 (리스트) 반환
    except Exception as e:
        logger.error(f"대화 기록 조회 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="대화 기록 조회 중 오류가 발생했습니다.")

@router.post("/chat")
async def handle_chat(user_message: UserMessage):
    logger.info(f"채팅 요청 받음 (라우터): ConvID={user_message.conversation_id}, Msg={user_message.message}")
    if not user_message.message:
        logger.warning("빈 메시지로 채팅 요청 받음 (라우터)")
        raise HTTPException(status_code=400, detail="메시지가 없습니다.")
    if not user_message.conversation_id:
        logger.warning("conversation_id 없이 채팅 요청 받음 (라우터)")
        raise HTTPException(status_code=400, detail="conversation_id가 필요합니다.")

    try:
        # 1. 사용자 메시지 저장
        await save_chat_message(user_message.conversation_id, "user", user_message.message)

        # 2. OpenAI 서비스 호출 (이제 conversation_id 전달)
        bot_response = await get_chat_response(user_message.conversation_id, user_message.message)

        # 3. 봇 응답 저장
        await save_chat_message(user_message.conversation_id, "assistant", bot_response)

        return {"response": bot_response}
    except ConnectionError as e:
        # 서비스에서 발생시킨 예외를 여기서 처리
        logger.error(f"서비스 연결 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # 기타 예외 처리
        logger.error(f"채팅 처리 중 예상치 못한 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="챗봇 응답 처리 중 오류가 발생했습니다.")