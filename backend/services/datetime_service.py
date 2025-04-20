import datetime
import logging
from typing import Dict
# zoneinfo 추가 (Python 3.9+)
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

logger = logging.getLogger(__name__)

# 한국 시간대 정의
KST = None
try:
    KST = ZoneInfo("Asia/Seoul")
except ZoneInfoNotFoundError:
    logger.error("'Asia/Seoul' 시간대를 찾을 수 없습니다. 시스템에 시간대 데이터가 설치되어 있는지 확인하세요.")
    # 또는 pytz 라이브러리를 대신 사용할 수 있습니다.

async def get_current_date() -> Dict[str, str]:
    """현재 한국 시간(KST) 기준 날짜를 'YYYY-MM-DD' 형식으로 반환합니다."""
    if KST is None:
        return {"error": "한국 시간대 정보를 로드할 수 없습니다."}
    try:
        # KST 기준으로 현재 시간 가져오기
        now_kst = datetime.datetime.now(KST)
        # 날짜 부분만 추출
        today_kst = now_kst.date()
        date_str = today_kst.strftime("%Y-%m-%d")
        logger.info(f"현재 한국 날짜 조회 성공: {date_str}")
        return {"current_date": date_str}
    except Exception as e:
        logger.error(f"현재 한국 날짜 조회 중 오류 발생: {e}", exc_info=True)
        return {"error": "현재 날짜를 가져오는 중 오류가 발생했습니다."}