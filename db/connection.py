import config
from motor import AsyncIOMotorClient
from umongo import Document, Instance, fields, validate

db = AsyncIOMotorClient()[config.mongo_collection]
mongo = Instance(db)
