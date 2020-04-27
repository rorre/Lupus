import asyncio
import json

import aiohttp


class NekoClient:
    BASE_URL = "https://nekos.life/api/v2/img/"

    def __init__(self, session=None, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.session = session or aiohttp.ClientSession(loop=loop)

    async def get(self, endpoint):
        url = self.BASE_URL + endpoint
        async with self.session.get(url) as response:
            js_text = await response.text() or "{}"
            return json.loads(js_text)
