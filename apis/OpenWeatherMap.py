import asyncio
from typing import List
from urllib.parse import urlencode

import aiohttp
from aiocache import cached, Cache
from aiocache.serializers import PickleSerializer


class RateLimitedException(Exception):
    pass


class OWMException(Exception):
    pass


class Weather:
    def __init__(self, js):
        self.coord: dict = js.get("coord", None)
        self.weather: List = js.get("weather", [])
        self.base: str = js.get("base", None)
        self.main: dict = js.get("main", None)
        self.visibility: int = js.get("visibility", None)
        self.wind: dict = js.get("wind", None)
        self.clouds: dict = js.get("clouds", None)
        self.dt: int = js.get("dt", None)
        self.sys: dict = js.get("sys", None)
        self.timezone: int = js.get("timezone", None)
        self.id: int = js.get("id", None)
        self.name: str = js.get("name", None)
        self.cod: int = js.get("cod", None)


class Forecast:
    def __init__(self, js):
        self.cod: str = js.get("cod", None)
        self.message: int = js.get("message", None)
        self.cnt: int = js.get("cnt", None)
        self.forecasts: List = list(map(Weather, js.get("list", [])))
        self.city: dict = js.get("city", None)


class OWMClient:
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    WEATHER_URL = BASE_URL + "/weather"
    FORECAST_URL = BASE_URL + "/forecast"

    def __init__(self, key, session=None, loop=None):
        self._key = key
        self.loop = loop or asyncio.get_event_loop()
        self.session = session or aiohttp.ClientSession(loop=loop)

    async def _call_api(self, url, **kwargs):
        query_string = self._generate_query_keys(**kwargs)
        url += "?" + query_string

        async with self.session.get(url) as response:
            js = await response.json()
            code = js.get("cod")
            if code != 200:
                if js.get("cod") == 429:
                    raise RateLimitedException("Limit already passed.")
                raise OWMException(js.get("message", "Server tripped."))
            return js

    def _generate_query_keys(self, **kwargs) -> str:
        queries = {"appid": self._key}
        for k, v in kwargs.items():
            if v:
                queries[k] = v
        return urlencode(queries)

    @cached(ttl=300, cache=Cache.REDIS, key="weather", serializer=PickleSerializer(), port=6379, namespace="main")
    async def get_weather(self, place, units="metric"):
        res = await self._call_api(self.WEATHER_URL, q=place, units=units)
        return Weather(res)

    @cached(ttl=300, cache=Cache.REDIS, key="forecast", serializer=PickleSerializer(), port=6379, namespace="main")
    async def get_forecast(self, place, units="metric"):
        res = await self._call_api(self.FORECAST_URL, q=place, units=units)
        return Forecast(res)
