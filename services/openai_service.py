import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

# MongoDB 함수 임포트
from db.mongo import get_chat_history

load_dotenv()

logger = logging.getLogger(__name__)

# .env 파일에서 API 키 로드
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    raise ValueError("OPENAI_API_KEY 환경 변수를 설정해야 합니다.")

try:
    client = OpenAI(api_key=api_key)
    logger.info("OpenAI 클라이언트 초기화 성공")
except Exception as e:
    logger.error(f"OpenAI 클라이언트 초기화 중 오류 발생: {e}", exc_info=True)
    raise

# 참고: 'gpt-4.1-nano'
MODEL_NAME = "gpt-4.1-nano"
SYSTEM_PROMPT = "You are a helpful assistant."
# 대화 기록 길이 제한 (토큰 제한 고려)
HISTORY_LIMIT = 10

async def get_chat_response(conversation_id: str, message: str) -> str:
    """사용자 메시지와 대화 ID를 받아 OpenAI 챗봇 응답을 반환합니다.
       대화 기록을 조회하여 맥락을 포함합니다.
    """
    if not message:
        logger.warning("빈 메시지로 응답 생성 시도")
        # 서비스 레벨에서도 기본적인 입력 검증을 할 수 있습니다.
        # 혹은 라우트에서 처리된 것으로 가정할 수도 있습니다.
        return "메시지를 입력해주세요."

    try:
        # 1. MongoDB에서 대화 기록 조회
        history = await get_chat_history(conversation_id, limit=HISTORY_LIMIT)

        # 2. OpenAI API 요청 메시지 구성
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        messages.extend(history) # 이전 대화 내용 추가
        messages.append({"role": "user", "content": message}) # 현재 사용자 메시지 추가

        logger.info(f"OpenAI API 호출 시작 (모델: {MODEL_NAME}, ConvID: {conversation_id}, History: {len(history)} messages)")
        # logger.debug(f"API 요청 메시지: {messages}") # 디버깅 시 메시지 내용 확인

        # 3. OpenAI API 호출
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages
        )
        bot_message = response.choices[0].message.content
        logger.info("OpenAI API 응답 성공")
        return bot_message
    except Exception as e:
        logger.error(f"OpenAI API 호출 중 오류 발생: {e}", exc_info=True)
        # 여기서 예외를 다시 발생시켜 라우트에서 처리하도록 합니다.
        raise ConnectionError("챗봇 서비스와의 통신 중 오류가 발생했습니다.") from e