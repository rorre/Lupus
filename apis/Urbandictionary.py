import asyncio

import aiohttp


class UrbanDef:
    def __init__(self, js):
        self.definition = js.get("definition")
        self.example = js.get("example")
        self.thumbs_down = js.get("thumbs_down", 0)
        self.thumbs_up = js.get("thumbs_up", 0)
        self.word = js.get("word")
        self.permalink = js.get("permalink")
        self.sound_urls = js.get("sound_urls")
        self.author = js.get("author")
        self.defid = js.get("defid")
        self.written_on = js.get("written_on")


class UrbanClient:
    DEFINE_URL = "https://api.urbandictionary.com/v0/define?term="
    DEFID_URL = "https://api.urbandictionary.com/v0/define?defid="
    RANDOM_URL = "https://api.urbandictionary.com/v0/random"

    def __init__(self, session=None, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.session = session or aiohttp.ClientSession(loop=loop)

    async def _call_api(self, url):
        async with self.session.get(url) as response:
            js = await response.json()
            if not js or any(err in js for err in ("error", "errors")):
                raise ValueError("Invalid input")
            if "list" not in js or not js["list"]:
                return []
            return list(map(UrbanDef, js["list"]))

    def search_term(self, query):
        url = self.DEFINE_URL + query
        return self._call_api(url)

    def definition(self, defid):
        url = self.DEFINE_URL + defid
        return self._call_api(url)

    def random(self):
        return self._call_api(self.RANDOM_URL)
