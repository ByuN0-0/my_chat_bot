from pydantic import BaseModel

class UserMessage(BaseModel):
    conversation_id: str
    message: str