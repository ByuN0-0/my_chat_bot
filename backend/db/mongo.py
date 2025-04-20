import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Optional, List

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017") # Docker 환경 고려
DB_NAME = "chatbot_db"
COLLECTION_NAME = "chat_history"

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None
    collection = None

mongo_db = MongoDB()

async def connect_to_mongo():
    """애플리케이션 시작 시 MongoDB에 연결합니다."""
    logger.info("MongoDB 연결 시도 중...")
    try:
        mongo_db.client = AsyncIOMotorClient(MONGO_URI)
        mongo_db.db = mongo_db.client[DB_NAME]
        mongo_db.collection = mongo_db.db[COLLECTION_NAME]
        # 연결 테스트 (옵션)
        await mongo_db.client.admin.command('ping')
        logger.info("MongoDB 연결 성공!")
    except Exception as e:
        logger.error(f"MongoDB 연결 실패: {e}", exc_info=True)
        # 연결 실패 시 애플리케이션을 중단할 수도 있습니다.
        raise

async def close_mongo_connection():
    """애플리케이션 종료 시 MongoDB 연결을 닫습니다."""
    if mongo_db.client:
        mongo_db.client.close()
        logger.info("MongoDB 연결 종료됨.")

async def save_chat_message(
    conversation_id: str,
    role: str,
    content: str,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    cost: Optional[float] = None
):
    """채팅 메시지와 관련 메타데이터(토큰, 비용 등)를 MongoDB에 저장합니다."""
    if mongo_db.collection is None:
        logger.error("MongoDB 컬렉션이 초기화되지 않았습니다. 메시지 저장 실패.")
        return
    try:
        message_doc = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        }
        if prompt_tokens is not None:
            message_doc["prompt_tokens"] = prompt_tokens
        if completion_tokens is not None:
            message_doc["completion_tokens"] = completion_tokens
        if cost is not None:
            message_doc["cost"] = cost

        await mongo_db.collection.insert_one(message_doc)
        log_extra = f", Tokens: P={prompt_tokens} C={completion_tokens}, Cost: ${cost:.6f}" if cost is not None else ""
        logger.debug(f"메시지 저장됨: ConvID={conversation_id}, Role={role}{log_extra}")
    except Exception as e:
        logger.error(f"메시지 저장 실패: {e}", exc_info=True)

async def get_chat_history(conversation_id: str, limit: int = 10) -> list:
    """특정 대화 ID의 최근 채팅 기록을 가져옵니다."""
    if mongo_db.collection is None:
        logger.error("MongoDB 컬렉션이 초기화되지 않았습니다. 기록 조회 실패.")
        return []
    try:
        # timestamp 기준으로 내림차순 정렬 후 제한된 개수만큼 가져옴
        cursor = mongo_db.collection.find(
            {"conversation_id": conversation_id}
        ).sort("timestamp", -1).limit(limit)
        # 시간 순서대로 다시 뒤집어서 반환 (오래된 메시지가 먼저 오도록)
        history = await cursor.to_list(length=limit)
        history.reverse()
        logger.debug(f"{len(history)}개의 채팅 기록 조회됨: ConvID={conversation_id}")
        # OpenAI API 형식에 맞게 content와 role만 추출
        return [{"role": msg["role"], "content": msg["content"]} for msg in history]
    except Exception as e:
        logger.error(f"채팅 기록 조회 실패: {e}", exc_info=True)
        return []

async def get_all_sessions() -> list:
    """MongoDB에서 고유한 conversation_id 목록을 가져옵니다."""
    if mongo_db.collection is None:
        logger.error("MongoDB 컬렉션이 초기화되지 않았습니다. 세션 목록 조회 실패.")
        return []
    try:
        # 가장 최근 메시지 타임스탬프와 함께 고유 ID를 가져옵니다.
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
        sessions = await mongo_db.collection.aggregate(pipeline).to_list(length=None) # 모든 결과 가져오기
        session_ids = [s["conversation_id"] for s in sessions]
        logger.info(f"{len(session_ids)}개의 세션 목록 조회됨")
        return session_ids
    except Exception as e:
        logger.error(f"세션 목록 조회 실패: {e}", exc_info=True)
        return []

async def get_daily_usage_stats() -> List[dict]:
    """일별 토큰 사용량 및 비용 통계를 집계합니다."""
    if mongo_db.collection is None:
        logger.error("MongoDB 컬렉션 없음 - 일별 통계 조회 실패")
        return []
    try:
        pipeline = [
            {
                "$match": { # assistant 역할의 문서만, 토큰/비용 필드 존재하는 것만
                    "role": "assistant",
                    "prompt_tokens": { "$exists": True },
                    "completion_tokens": { "$exists": True },
                    "cost": { "$exists": True }
                }
            },
            {
                "$group": {
                    "_id": {
                        # UTC 기준 날짜로 그룹화 (YYYY-MM-DD)
                        "$dateToString": { "format": "%Y-%m-%d", "date": "$timestamp" }
                    },
                    "total_prompt_tokens": { "$sum": "$prompt_tokens" },
                    "total_completion_tokens": { "$sum": "$completion_tokens" },
                    "total_cost": { "$sum": "$cost" }
                }
            },
            {
                "$project": { # 결과 필드 이름 변경 및 형식 지정
                    "_id": 0,
                    "date": "$_id",
                    "prompt_tokens": "$total_prompt_tokens",
                    "completion_tokens": "$total_completion_tokens",
                    "cost": "$total_cost"
                }
            },
            { "$sort": { "date": 1 } } # 날짜 오름차순 정렬
        ]
        stats = await mongo_db.collection.aggregate(pipeline).to_list(length=None)
        logger.info(f"{len(stats)}개의 일별 통계 조회됨")
        return stats
    except Exception as e:
        logger.error(f"일별 통계 조회 실패: {e}", exc_info=True)
        return []

async def get_monthly_usage_stats() -> List[dict]:
    """월별 토큰 사용량 및 비용 통계를 집계합니다."""
    if mongo_db.collection is None:
        logger.error("MongoDB 컬렉션 없음 - 월별 통계 조회 실패")
        return []
    try:
        pipeline = [
            {
                "$match": {
                    "role": "assistant",
                    "prompt_tokens": { "$exists": True },
                    "completion_tokens": { "$exists": True },
                    "cost": { "$exists": True }
                }
            },
            {
                "$group": {
                    "_id": {
                        # UTC 기준 월로 그룹화 (YYYY-MM)
                        "$dateToString": { "format": "%Y-%m", "date": "$timestamp" }
                    },
                    "total_prompt_tokens": { "$sum": "$prompt_tokens" },
                    "total_completion_tokens": { "$sum": "$completion_tokens" },
                    "total_cost": { "$sum": "$cost" }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "month": "$_id",
                    "prompt_tokens": "$total_prompt_tokens",
                    "completion_tokens": "$total_completion_tokens",
                    "cost": "$total_cost"
                }
            },
            { "$sort": { "month": 1 } } # 월 오름차순 정렬
        ]
        stats = await mongo_db.collection.aggregate(pipeline).to_list(length=None)
        logger.info(f"{len(stats)}개의 월별 통계 조회됨")
        return stats
    except Exception as e:
        logger.error(f"월별 통계 조회 실패: {e}", exc_info=True)
        return []