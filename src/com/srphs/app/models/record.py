from beanie import Document, Link
from datetime import datetime
from typing import List
from .user import User
from pydantic import Field

class HealthRecord(Document):
    user_email: str
    prediction: str
    weight: float
    height: float
    top_recommendations: List[str]
    date: datetime = Field(default_factory=datetime.now)


    class Settings:
        name = "health_history"