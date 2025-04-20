import logging
from typing import List

# DB 함수 임포트
from db.mongo import get_daily_usage_stats as db_get_daily_usage
from db.mongo import get_monthly_usage_stats as db_get_monthly_usage

# 스키마 임포트 (타입 힌팅 및 데이터 구조 확인용)
from schemas.admin import DailyUsageStat, MonthlyUsageStat

logger = logging.getLogger(__name__)

async def get_daily_stats() -> List[DailyUsageStat]:
    """일별 사용량 통계를 조회합니다."""
    logger.info("일별 통계 서비스 호출됨")
    daily_data = await db_get_daily_usage()
    # DB 결과가 스키마와 호환되는지 확인 (여기서는 단순 반환)
    # 필요시 여기서 데이터 변환/검증 추가 가능
    return [DailyUsageStat(**stat) for stat in daily_data]

async def get_monthly_stats() -> List[MonthlyUsageStat]:
    """월별 사용량 통계를 조회합니다."""
    logger.info("월별 통계 서비스 호출됨")
    monthly_data = await db_get_monthly_usage()
    # DB 결과가 스키마와 호환되는지 확인 (여기서는 단순 반환)
    return [MonthlyUsageStat(**stat) for stat in monthly_data]