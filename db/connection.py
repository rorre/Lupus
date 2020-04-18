import config
from motor.motor_asyncio import AsyncIOMotorClient
from umongo import Instance

db = AsyncIOMotorClient()[config.mongo_collection]
mongo = Instance(db)
