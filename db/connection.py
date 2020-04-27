from motor.motor_asyncio import AsyncIOMotorClient
from umongo import Instance

import config

db = AsyncIOMotorClient()[config.mongo_collection]
mongo = Instance(db)
