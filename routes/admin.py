import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# 서비스 및 스키마 임포트
from services import admin_service
from schemas.admin import DailyUsageResponse, MonthlyUsageResponse

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/admin", # 모든 경로 앞에 /admin 추가
    tags=["admin"]    # API 문서 그룹화 태그
)

# 템플릿 설정 (admin.html 용)
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def admin_page(request: Request):
    """관리자 페이지 HTML을 반환합니다."""
    logger.info("관리자 페이지 요청 받음")
    # admin.html 템플릿 렌더링 (아직 생성 전)
    return templates.TemplateResponse("admin.html", {"request": request})

@router.get("/usage/daily", response_model=DailyUsageResponse)
async def get_daily_usage_route():
    """일별 사용량 통계를 반환하는 API 엔드포인트"""
    logger.info("일별 사용량 API 요청 받음")
    try:
        stats = await admin_service.get_daily_stats()
        return DailyUsageResponse(daily_stats=stats)
    except Exception as e:
        logger.error(f"일별 사용량 API 처리 중 오류: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="일별 사용량 조회 중 서버 오류 발생")

@router.get("/usage/monthly", response_model=MonthlyUsageResponse)
async def get_monthly_usage_route():
    """월별 사용량 통계를 반환하는 API 엔드포인트"""
    logger.info("월별 사용량 API 요청 받음")
    try:
        stats = await admin_service.get_monthly_stats()
        return MonthlyUsageResponse(monthly_stats=stats)
    except Exception as e:
        logger.error(f"월별 사용량 API 처리 중 오류: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="월별 사용량 조회 중 서버 오류 발생")