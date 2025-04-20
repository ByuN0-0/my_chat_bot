import logging

# 의존성 주입을 위해 필요한 모듈 임포트
from db.mongo import save_chat_message, mongo_db # mongo_db 임포트 확인
from services.openai_service import get_chat_response, MODEL_NAME # MODEL_NAME 임포트 (가격 계산에 필요할 수 있음)
from schemas.token_usage import TokenUsage # 절대 경로로 수정

logger = logging.getLogger(__name__)

# === 비용 계산 상수 (GPT-4.1 nano 기준, 2025-04-20 사용자 제공 정보) ===
# 입력: $0.100 / 1M tokens => $0.0001 / 1K tokens
PRICE_PER_1K_TOKENS_PROMPT = 0.0001
# 출력: $0.400 / 1M tokens => $0.0004 / 1K tokens
PRICE_PER_1K_TOKENS_COMPLETION = 0.0004

def calculate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """토큰 수를 기반으로 예상 비용을 계산합니다."""
    if prompt_tokens == 0 and completion_tokens == 0:
        return 0.0

    prompt_cost = (prompt_tokens / 1000) * PRICE_PER_1K_TOKENS_PROMPT
    completion_cost = (completion_tokens / 1000) * PRICE_PER_1K_TOKENS_COMPLETION
    total_cost = prompt_cost + completion_cost
    logger.debug(f"비용 계산: Prompt={prompt_tokens} (${prompt_cost:.6f}), Completion={completion_tokens} (${completion_cost:.6f}), Total=${total_cost:.6f}")
    return total_cost

async def handle_new_message(conversation_id: str, user_message: str) -> str:
    """새로운 사용자 메시지를 처리하고, 토큰 사용량과 비용을 기록합니다."""
    logger.info(f"채팅 서비스 시작: ConvID={conversation_id}")

    # 1. 사용자 메시지 저장 (토큰/비용 정보 없음)
    await save_chat_message(conversation_id, "user", user_message)
    logger.debug(f"사용자 메시지 저장 완료: ConvID={conversation_id}")

    # 2. OpenAI 서비스 호출 (봇 응답 + 토큰 정보 받기)
    bot_response, prompt_tokens, completion_tokens = await get_chat_response(conversation_id, user_message)
    logger.debug(f"봇 응답 및 토큰 수신 완료: ConvID={conversation_id}")

    # 3. 비용 계산 (별도 저장 위해 계산은 유지)
    cost = calculate_cost(prompt_tokens, completion_tokens)

    # 3.5 토큰 사용량 MongoDB의 'token_usages' 컬렉션에 저장 (이전 단계에서 추가됨)
    token_usage_data = TokenUsage(
        session_id=conversation_id,
        model_name=MODEL_NAME, # openai_service 에서 가져온 모델 이름 사용
        input_tokens=prompt_tokens,
        output_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens
        # user_id 필드는 필요시 추가 구현
        # cost 필드는 TokenUsage 스키마에 없으므로 저장 안 함 (필요 시 스키마 수정)
    )
    try:
        # mongo_db 객체를 통해 동적으로 컬렉션 접근
        await mongo_db.db['token_usages'].insert_one(token_usage_data.dict(by_alias=True, exclude_none=True))
        logger.debug(f"토큰 사용량 저장 완료: ConvID={conversation_id}, Model={MODEL_NAME}, In={prompt_tokens}, Out={completion_tokens}")
    except Exception as e:
        logger.error(f"토큰 사용량 저장 실패: ConvID={conversation_id}, Error: {e}", exc_info=True)
        # 토큰 저장 실패가 챗봇 흐름을 막지 않도록 처리 (로깅만 함)

    # 4. 봇 응답 저장 ('chat_history' 컬렉션) - 토큰/비용 정보 제외
    await save_chat_message(
        conversation_id=conversation_id,
        role="assistant",
        content=bot_response
        # prompt_tokens=prompt_tokens, # 제거
        # completion_tokens=completion_tokens, # 제거
        # cost=cost # 제거
    )
    logger.debug(f"봇 응답 저장 완료 (메시지만): ConvID={conversation_id}")

    # 5. 봇 응답 반환
    return bot_response