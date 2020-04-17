from motor import AsyncIOMotorClient
from umongo import Instance, Document, fields, validate

import config

db = AsyncIOMotorClient()[config.mongo_collection]
mongo = Instance(db)
