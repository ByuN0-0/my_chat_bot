import os
import logging
import json # JSON 파싱 추가
from typing import Tuple, List, Dict, Any # List, Dict, Any 추가
from openai import OpenAI, AssistantEventHandler # 필요한 클래스 추가

# MongoDB 함수 임포트
from db.mongo import get_chat_history
# 날씨 서비스 함수 임포트
from services.weather_service import get_current_weather

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
SYSTEM_PROMPT = "당신은 사용자의 개인 비서입니다. 실시간 날씨를 조회하는 등의 도구를 사용할 수 있습니다."
# 대화 기록 길이 제한 (토큰 제한 고려)
HISTORY_LIMIT = 10

# === 도구 정의 (OpenWeatherMap 날씨 조회 - 위도/경도 사용) ===
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a given latitude and longitude",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "The latitude of the location",
                    },
                    "longitude": {
                        "type": "number",
                        "description": "The longitude of the location",
                    },
                },
                "required": ["latitude", "longitude"],
            },
        },
    }
]

async def get_chat_response(conversation_id: str, message: str) -> Tuple[str, int, int]:
    """사용자 메시지를 받아 OpenAI 챗봇 응답과 총 토큰 사용량을 반환합니다.
      필요시 날씨 조회 도구(위도/경도 기반)를 사용합니다.
    """
    if not message:
        logger.warning("빈 메시지로 응답 생성 시도")
        return "메시지를 입력해주세요.", 0, 0

    try:
        history = await get_chat_history(conversation_id, limit=HISTORY_LIMIT)
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        logger.info(f"OpenAI API 호출 시작 (모델: {MODEL_NAME}, ConvID: {conversation_id})")

        # === 첫 번째 API 호출 ===
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
            tool_choice="auto", # LLM이 도구 사용 여부 결정
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        # 누적 토큰 계산용 변수 초기화
        total_prompt_tokens = response.usage.prompt_tokens
        total_completion_tokens = response.usage.completion_tokens

        # === 도구 사용 분기 ===
        if tool_calls:
            logger.info(f"도구 호출 감지: {tool_calls}")
            available_functions = {
                "get_current_weather": get_current_weather,
            }
            # 어시스턴트의 응답(tool_calls 포함)을 메시지 목록에 추가
            messages.append(response_message.model_dump(exclude_unset=True))

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions.get(function_name)
                if not function_to_call:
                    logger.error(f"알 수 없는 함수 호출 시도: {function_name}")
                    # 오류 상황 처리 (예: 사용자에게 알림)
                    tool_result = {"error": f"Function '{function_name}' not found."}
                else:
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                        # 위도/경도 인자 추출
                        latitude = function_args.get("latitude")
                        longitude = function_args.get("longitude")
                        logger.info(f"함수 '{function_name}' 호출 (인자: lat={latitude}, lon={longitude})")
                        # location 대신 lat, lon 전달
                        tool_result = await function_to_call(lat=latitude, lon=longitude)
                        logger.info(f"함수 '{function_name}' 결과: {tool_result}")
                    except json.JSONDecodeError:
                        logger.error(f"함수 인자 파싱 오류: {tool_call.function.arguments}")
                        tool_result = {"error": "Invalid function arguments."}
                    except Exception as e:
                        logger.error(f"함수 '{function_name}' 실행 중 오류: {e}", exc_info=True)
                        tool_result = {"error": "Error executing function."}

                # 도구 실행 결과를 메시지 목록에 추가
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(tool_result), # 결과를 JSON 문자열로 전달
                    }
                )

            # === 두 번째 API 호출 (도구 결과 포함) ===
            logger.info("도구 결과 포함하여 두 번째 API 호출 시작")
            second_response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
            )
            final_response = second_response.choices[0].message.content
            # 두 번째 호출의 토큰 사용량 누적
            total_prompt_tokens += second_response.usage.prompt_tokens
            total_completion_tokens += second_response.usage.completion_tokens
            logger.info(f"두 번째 API 응답 성공. 누적 Tokens: Prompt={total_prompt_tokens}, Completion={total_completion_tokens}")

            return final_response, total_prompt_tokens, total_completion_tokens

        else:
            # 도구를 사용하지 않은 경우, 첫 번째 응답 반환
            logger.info(f"도구 사용 없음. 첫 번째 API 응답 반환. Tokens: Prompt={total_prompt_tokens}, Completion={total_completion_tokens}")
            final_response = response_message.content
            return final_response, total_prompt_tokens, total_completion_tokens

    except Exception as e:
        logger.error(f"OpenAI 서비스 처리 중 오류 발생: {e}", exc_info=True)
        raise ConnectionError("챗봇 서비스와의 통신 중 오류가 발생했습니다.") from e