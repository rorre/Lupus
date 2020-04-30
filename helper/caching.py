from aiocache import Cache
from aiocache.serializers import PickleSerializer

cache = Cache(Cache.REDIS, endpoint="127.0.0.1", port=6379, namespace="main", serializer=PickleSerializer())
#cache = Cache(serializer=PickleSerializer())
