from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic_core import core_schema
from datetime import datetime
from typing import Optional, Any
from bson import ObjectId

# ObjectId를 Pydantic에서 사용하기 위한 커스텀 타입 (Pydantic V2 스타일)
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _info): # Pydantic V2 validator 시그니처
        if isinstance(v, ObjectId):
            return v
        if ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> dict[str, Any]:
        # JSON 스키마에서 ObjectId를 문자열 타입으로 표현하도록 수정
        json_schema = handler(core_schema.str_schema())
        json_schema.update(example='5eb7cf5a86d9755df3a6c593') # 예시 추가
        return json_schema

# 토큰 사용량 스키마 정의
class TokenUsage(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: Optional[str] = None # 사용자별 추적이 필요하면 사용
    session_id: Optional[str] = None # 특정 대화 세션 ID
    model_name: str = Field(...)
    input_tokens: int = Field(...)
    output_tokens: int = Field(...)
    total_tokens: int = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True # Pydantic V2 스타일 이름 변경
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
        json_schema_extra = { # Pydantic V2 스타일 이름 변경
            "example": {
                "_id": "5eb7cf5a86d9755df3a6c593",
                "session_id": "conv_12345",
                "model_name": "gpt-4-turbo",
                "input_tokens": 150,
                "output_tokens": 200,
                "total_tokens": 350,
                "timestamp": "2023-10-27T10:00:00Z"
            }
        }
