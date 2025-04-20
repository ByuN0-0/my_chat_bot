import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse # JSONResponse 추가
from fastapi.templating import Jinja2Templates
from typing import List # List 추가

# 스키마 임포트
from schemas.chat import UserMessage
from schemas.session import SessionListResponse # 세션 스키마 임포트

# 서비스 임포트
from services import chat_service, session_service # 개별 서비스 임포트

logger = logging.getLogger(__name__)
router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    logger.info("루트 페이지 요청 받음 (라우터)")
    return templates.TemplateResponse("index.html", {"request": request})

# 세션 목록 엔드포인트 (서비스 호출 및 응답 모델 사용)
@router.get("/sessions", response_model=SessionListResponse)
async def get_sessions_route():
    logger.info("세션 목록 라우트 호출됨")
    try:
        session_ids = await session_service.get_sessions()
        return SessionListResponse(sessions=session_ids)
    except Exception as e:
        # 서비스 레벨에서 처리되지 않은 예외
        logger.error(f"세션 목록 라우트 처리 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="세션 목록 조회 중 서버 오류가 발생했습니다.")

# 대화 기록 조회 엔드포인트 (서비스 호출 및 응답 타입 명시)
# 참고: Pydantic 모델을 정의하여 response_model로 사용하는 것이 더 엄격하지만, 여기서는 List[dict]를 사용
@router.get("/history/{conversation_id}", response_model=List[dict])
async def get_history_route(conversation_id: str):
    logger.info(f"대화 기록 라우트 호출됨: ConvID={conversation_id}")
    if not conversation_id:
        # 기본적인 입력 검증은 라우터에서 수행
        raise HTTPException(status_code=400, detail="conversation_id가 필요합니다.")

    try:
        history = await session_service.get_history(conversation_id)
        return history
    except Exception as e:
        # 서비스 레벨에서 처리되지 않은 예외
        logger.error(f"대화 기록 라우트 처리 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="대화 기록 조회 중 서버 오류가 발생했습니다.")

# 채팅 엔드포인트 (서비스 호출)
@router.post("/chat", response_class=JSONResponse)
async def handle_chat_route(user_message: UserMessage):
    logger.info(f"채팅 라우트 호출됨: ConvID={user_message.conversation_id}")
    # Pydantic 모델을 통해 conversation_id 와 message 는 이미 검증됨 (존재 여부, 타입)
    # 빈 문자열 등 추가 검증이 필요하면 여기서 수행 가능
    if not user_message.message:
        raise HTTPException(status_code=400, detail="메시지 내용이 비어있습니다.")
    if not user_message.conversation_id:
        raise HTTPException(status_code=400, detail="conversation_id가 비어있습니다.")

    try:
        # chat_service 호출
        bot_response = await chat_service.handle_new_message(
            conversation_id=user_message.conversation_id,
            user_message=user_message.message
        )
        return {"response": bot_response}
    except ConnectionError as e:
        # 서비스에서 발생시킨 특정 예외 처리
        logger.error(f"OpenAI 서비스 연결 오류 발생 (라우트): {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"챗봇 서비스 연결 오류: {e}") # 503 Service Unavailable
    except Exception as e:
        # 기타 예상치 못한 오류
        logger.error(f"채팅 라우트 처리 중 예상치 못한 오류 발생: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="챗봇 응답 처리 중 서버 오류가 발생했습니다.")