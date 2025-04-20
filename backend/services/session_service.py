import logging
from typing import List

# 의존성 주입
from db.mongo import get_all_sessions as db_get_all_sessions
from db.mongo import get_chat_history as db_get_chat_history

logger = logging.getLogger(__name__)

async def get_sessions() -> List[str]:
    """모든 세션 ID 목록을 반환합니다."""
    logger.info("세션 목록 조회 서비스 호출됨")
    # 데이터베이스 함수 직접 호출
    session_ids = await db_get_all_sessions()
    return session_ids

async def get_history(conversation_id: str) -> List[dict]:
    """특정 세션의 채팅 기록을 반환합니다."""
    logger.info(f"채팅 기록 조회 서비스 호출됨: ConvID={conversation_id}")
    # 데이터베이스 함수 직접 호출
    history = await db_get_chat_history(conversation_id)
    return history