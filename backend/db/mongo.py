import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Optional, List

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017") # Docker 환경 고려
DB_NAME = "chatbot_db"
COLLECTION_NAME_CHAT = "chat_history"
COLLECTION_NAME_TOKENS = "token_usages" # 토큰 컬렉션 이름 정의

# === 비용 계산 상수 (GPT-4.1 nano 기준) ===
PRICE_PER_TOKEN_INPUT = 0.100 / 1_000_000
PRICE_PER_TOKEN_OUTPUT = 0.400 / 1_000_000

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None
    chat_collection = None # 명시적으로 구분
    token_collection = None # 명시적으로 구분

mongo_db = MongoDB()

async def connect_to_mongo():
    """애플리케이션 시작 시 MongoDB에 연결하고 컬렉션 및 인덱스를 설정합니다.""" # 설명 업데이트
    logger.info("MongoDB 연결 시도 중...")
    try:
        mongo_db.client = AsyncIOMotorClient(MONGO_URI)
        mongo_db.db = mongo_db.client[DB_NAME]
        mongo_db.chat_collection = mongo_db.db[COLLECTION_NAME_CHAT]
        mongo_db.token_collection = mongo_db.db[COLLECTION_NAME_TOKENS] # 토큰 컬렉션 할당

        # 연결 테스트
        await mongo_db.client.admin.command('ping')
        logger.info("MongoDB 연결 성공!")

        # --- 인덱스 생성 --- #
        # chat_history 컬렉션 인덱스 (세션 조회 및 기록 조회 최적화)
        await mongo_db.chat_collection.create_index([("conversation_id", 1), ("timestamp", -1)])
        logger.info(f"'{COLLECTION_NAME_CHAT}' 컬렉션 인덱스 생성/확인 완료.")

        # token_usages 컬렉션 인덱스 (세션별 조회 및 시간순 조회 최적화)
        await mongo_db.token_collection.create_index([("session_id", 1)])
        await mongo_db.token_collection.create_index([("timestamp", -1)])
        logger.info(f"'{COLLECTION_NAME_TOKENS}' 컬렉션 인덱스 생성/확인 완료.")

    except Exception as e:
        logger.error(f"MongoDB 연결 또는 인덱스 생성 실패: {e}", exc_info=True)
        raise

async def close_mongo_connection():
    """애플리케이션 종료 시 MongoDB 연결을 닫습니다."""
    if mongo_db.client:
        mongo_db.client.close()
        logger.info("MongoDB 연결 종료됨.")

async def save_chat_message(
    conversation_id: str,
    role: str,
    content: str
):
    """채팅 메시지를 MongoDB에 저장합니다."""
    if mongo_db.chat_collection is None: # chat_collection 확인
        logger.error("MongoDB chat 컬렉션이 초기화되지 않았습니다. 메시지 저장 실패.")
        return
    try:
        message_doc = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        }

        await mongo_db.chat_collection.insert_one(message_doc) # chat_collection 사용
        logger.debug(f"메시지 저장됨: ConvID={conversation_id}, Role={role}")
    except Exception as e:
        logger.error(f"메시지 저장 실패: {e}", exc_info=True)

async def get_chat_history(conversation_id: str, limit: int = 10) -> list:
    """특정 대화 ID의 최근 채팅 기록을 가져옵니다."""
    if mongo_db.chat_collection is None: # chat_collection 확인
        logger.error("MongoDB chat 컬렉션이 초기화되지 않았습니다. 기록 조회 실패.")
        return []
    try:
        cursor = mongo_db.chat_collection.find( # chat_collection 사용
            {"conversation_id": conversation_id}
        ).sort("timestamp", -1).limit(limit)
        history = await cursor.to_list(length=limit)
        history.reverse()
        logger.debug(f"{len(history)}개의 채팅 기록 조회됨: ConvID={conversation_id}")
        return [{"role": msg["role"], "content": msg["content"]} for msg in history]
    except Exception as e:
        logger.error(f"채팅 기록 조회 실패: {e}", exc_info=True)
        return []

async def get_all_sessions() -> list:
    """MongoDB에서 고유한 conversation_id 목록을 가져옵니다."""
    if mongo_db.chat_collection is None: # chat_collection 확인
        logger.error("MongoDB chat 컬렉션이 초기화되지 않았습니다. 세션 목록 조회 실패.")
        return []
    try:
        pipeline = [
            { "$sort": { "timestamp": -1 } }, # 시간 역순 정렬
            {
                "$group": {
                    "_id": "$conversation_id",
                    "last_message_time": { "$first": "$timestamp" }
                }
            },
            { "$sort": { "last_message_time": -1 } }, # 가장 최근 세션이 위로 오도록 정렬
            { "$project": { "_id": 0, "conversation_id": "$_id" } } # conversation_id 필드만 선택
        ]
        sessions = await mongo_db.chat_collection.aggregate(pipeline).to_list(length=None) # chat_collection 사용
        session_ids = [s["conversation_id"] for s in sessions]
        logger.info(f"{len(session_ids)}개의 세션 목록 조회됨")
        return session_ids
    except Exception as e:
        logger.error(f"세션 목록 조회 실패: {e}", exc_info=True)
        return []

async def get_daily_usage_stats() -> List[dict]:
    """일별 토큰 사용량 및 비용을 집계합니다.""" # 설명 수정
    if mongo_db.token_collection is None:
        logger.error("MongoDB token 컬렉션이 초기화되지 않았습니다. 일별 통계 조회 실패")
        return []
    try:
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "$dateToString": { "format": "%Y-%m-%d", "date": "$timestamp" }
                    },
                    "total_input_tokens": { "$sum": "$input_tokens" },
                    "total_output_tokens": { "$sum": "$output_tokens" },
                    "total_tokens": { "$sum": "$total_tokens" }
                    # 비용 계산은 $project 단계에서 합계된 토큰으로 수행
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "date": "$_id",
                    "input_tokens": "$total_input_tokens",
                    "output_tokens": "$total_output_tokens",
                    "total_tokens": "$total_tokens",
                    # 비용 계산 추가
                    "cost": {
                        "$add": [
                            { "$multiply": ["$total_input_tokens", PRICE_PER_TOKEN_INPUT] },
                            { "$multiply": ["$total_output_tokens", PRICE_PER_TOKEN_OUTPUT] }
                        ]
                    }
                }
            },
            { "$sort": { "date": 1 } }
        ]
        stats = await mongo_db.token_collection.aggregate(pipeline).to_list(length=None)
        logger.info(f"{len(stats)}개의 일별 사용량/비용 통계 조회됨") # 로그 메시지 수정
        return stats
    except Exception as e:
        logger.error(f"일별 사용량/비용 통계 조회 실패: {e}", exc_info=True) # 로그 메시지 수정
        return []

async def get_monthly_usage_stats() -> List[dict]:
    """월별 토큰 사용량 및 비용을 집계합니다.""" # 설명 수정
    if mongo_db.token_collection is None:
        logger.error("MongoDB token 컬렉션이 초기화되지 않았습니다. 월별 통계 조회 실패")
        return []
    try:
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "$dateToString": { "format": "%Y-%m", "date": "$timestamp" }
                    },
                    "total_input_tokens": { "$sum": "$input_tokens" },
                    "total_output_tokens": { "$sum": "$output_tokens" },
                    "total_tokens": { "$sum": "$total_tokens" }
                    # 비용 계산은 $project 단계에서
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "month": "$_id",
                    "input_tokens": "$total_input_tokens",
                    "output_tokens": "$total_output_tokens",
                    "total_tokens": "$total_tokens",
                    # 비용 계산 추가
                    "cost": {
                        "$add": [
                            { "$multiply": ["$total_input_tokens", PRICE_PER_TOKEN_INPUT] },
                            { "$multiply": ["$total_output_tokens", PRICE_PER_TOKEN_OUTPUT] }
                        ]
                    }
                }
            },
            { "$sort": { "month": 1 } }
        ]
        stats = await mongo_db.token_collection.aggregate(pipeline).to_list(length=None)
        logger.info(f"{len(stats)}개의 월별 사용량/비용 통계 조회됨") # 로그 메시지 수정
        return stats
    except Exception as e:
        logger.error(f"월별 사용량/비용 통계 조회 실패: {e}", exc_info=True) # 로그 메시지 수정
        return []

async def delete_chat_history_by_id(conversation_id: str) -> int:
    """Deletes all chat messages for a specific conversation ID."""
    if mongo_db.chat_collection is None: # chat_collection 확인
        logger.error("MongoDB chat 컬렉션이 초기화되지 않았습니다. 기록 삭제 실패.")
        raise ConnectionError("Database chat collection not available")
    if not conversation_id:
        logger.warning("삭제할 conversation_id가 제공되지 않았습니다.")
        return 0 # 삭제할 ID가 없으므로 0 반환

    try:
        delete_result = await mongo_db.chat_collection.delete_many({"conversation_id": conversation_id}) # chat_collection 사용
        deleted_count = delete_result.deleted_count
        logger.info(f"ConvID={conversation_id}의 채팅 기록 {deleted_count}개가 삭제되었습니다.")
        return deleted_count
    except Exception as e:
        logger.error(f"ConvID={conversation_id} 기록 삭제 중 오류 발생: {e}", exc_info=True)
        raise