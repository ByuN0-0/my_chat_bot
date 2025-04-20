import os
import logging
from typing import Tuple # Tuple 임포트
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

# gpt 4.1 nano
MODEL_NAME = "gpt-4.1-nano"
SYSTEM_PROMPT = "You are a helpful assistant."
# 대화 기록 길이 제한 (토큰 제한 고려)
HISTORY_LIMIT = 10

async def get_chat_response(conversation_id: str, message: str) -> Tuple[str, int, int]:
    """사용자 메시지와 대화 ID를 받아 OpenAI 챗봇 응답과 토큰 사용량을 반환합니다.

    Returns:
        Tuple[str, int, int]: (봇 응답 메시지, 프롬프트 토큰 수, 완료 토큰 수)
    """
    if not message:
        logger.warning("빈 메시지로 응답 생성 시도")
        # 빈 메시지 경우 토큰 0으로 반환
        return "메시지를 입력해주세요.", 0, 0

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

        # === 토큰 사용량 추출 ===
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens
        logger.info(f"OpenAI API 응답 성공. Tokens: Prompt={prompt_tokens}, Completion={completion_tokens}, Total={total_tokens}")

        return bot_message, prompt_tokens, completion_tokens

    except Exception as e:
        logger.error(f"OpenAI API 호출 중 오류 발생: {e}", exc_info=True)
        # 오류 발생 시에도 튜플 형태로 반환 (토큰 0)
        # raise ConnectionError(...) 대신 오류 메시지와 0 토큰 반환 고려 가능
        # 여기서는 기존처럼 예외를 발생시키고 라우트에서 처리
        raise ConnectionError("챗봇 서비스와의 통신 중 오류가 발생했습니다.") from e