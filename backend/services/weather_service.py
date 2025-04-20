import httpx
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

async def get_current_weather(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """지정된 위도/경도의 현재 날씨 정보를 OpenWeatherMap API로부터 가져옵니다."""
    if not API_KEY:
        logger.error("OpenWeatherMap API 키가 설정되지 않았습니다.")
        return {"error": "날씨 API 키가 설정되지 않아 날씨 정보를 가져올 수 없습니다."}
    if lat is None or lon is None:
        return {"error": "날씨를 조회할 위도와 경도가 필요합니다."}

    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric",  # 섭씨 온도 사용
        "lang": "kr"       # 한국어 설명
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BASE_URL, params=params)
            response.raise_for_status() # 오류 발생 시 예외 발생
            data = response.json()

            # 위치 이름을 응답에서 가져오거나, 위도/경도로 표시
            location_name = data.get("name")
            if not location_name or location_name.strip() == "":
                location_name = f"위도 {lat}, 경도 {lon}"

            # 필요한 정보 추출 및 가공 (예시)
            weather_info = {
                "location": location_name,
                "description": data["weather"][0]["description"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"]
            }
            logger.info(f"'{location_name}' ({lat}, {lon}) 날씨 정보 조회 성공: {weather_info}")
            return weather_info

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error(f"OpenWeatherMap API 키 인증 실패: {e}")
                return {"error": "날씨 API 키가 유효하지 않습니다."}
            elif e.response.status_code == 404:
                logger.warning(f"({lat}, {lon}) 위치를 찾을 수 없음: {e}")
                return {"error": f"해당 위도/경도({lat}, {lon})의 날씨 정보를 찾을 수 없습니다."}
            else:
                logger.error(f"OpenWeatherMap API 요청 실패 ({e.response.status_code}): {e}")
                return {"error": "날씨 정보를 가져오는 중 오류가 발생했습니다."}
        except Exception as e:
            logger.error(f"날씨 정보 조회 중 예상치 못한 오류: {e}", exc_info=True)
            return {"error": "날씨 정보를 처리하는 중 오류가 발생했습니다."}