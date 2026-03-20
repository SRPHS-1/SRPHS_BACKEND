from beanie import Document
from pydantic import EmailStr
from typing import Optional

class User(Document):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

    class Settings:
        name = "users" 