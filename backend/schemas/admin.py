from pydantic import BaseModel
from typing import List

class UsageStatBase(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    cost: float

class DailyUsageStat(UsageStatBase):
    date: str # YYYY-MM-DD

class MonthlyUsageStat(UsageStatBase):
    month: str # YYYY-MM

class DailyUsageResponse(BaseModel):
    daily_stats: List[DailyUsageStat]

class MonthlyUsageResponse(BaseModel):
    monthly_stats: List[MonthlyUsageStat]