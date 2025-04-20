import logging
from typing import List

# 의존성 주입
from db.mongo import get_all_sessions as db_get_all_sessions
from db.mongo import get_chat_history as db_get_chat_history
from db.mongo import delete_chat_history_by_id as db_delete_history

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

async def delete_session(conversation_id: str) -> int:
    """특정 세션 ID에 해당하는 모든 채팅 기록을 삭제합니다."""
    logger.info(f"세션 삭제 서비스 호출됨: ConvID={conversation_id}")
    if not conversation_id:
        logger.warning("삭제할 conversation_id가 제공되지 않았습니다.")
        raise ValueError("conversation_id is required")

    try:
        deleted_count = await db_delete_history(conversation_id)
        logger.info(f"세션 삭제 완료: ConvID={conversation_id}, 삭제된 메시지 수={deleted_count}")
        return deleted_count
    except Exception as e:
        logger.error(f"세션 삭제 중 오류 발생: ConvID={conversation_id}, Error: {e}", exc_info=True)
        raise