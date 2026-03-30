from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
from dotenv import load_dotenv
from ..models.user import User
from ..models.record import HealthRecord

load_dotenv()

async def init_db():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    await init_beanie(
        database=client.SRPHS_DB, 
        document_models=[User, HealthRecord]
    )