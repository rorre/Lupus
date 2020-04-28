import random
import re

import discord
from cachetools import LRUCache, TTLCache, cached
from discord.ext import commands

from helper import checks
from yippi import AsyncYippiClient

ESIX_REGEX = r"https:\/\/[www\.]*e[(?:621)(?:926)]+\.net\/posts\/(\d+)"
re_esix = re.compile(ESIX_REGEX)


class Furry(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = AsyncYippiClient("Lupus", "1.0", "Error-", loop=self.bot.loop)

    def _is_deleted(self, post):
        return post.flags["deleted"]

    def _generate_esix_embed(self, post):
        all_tags = []
        for k in post.tags:
            tags_category = post.tags[k]
            for tag in tags_category:
                all_tags.append(tag)
        tags_string = " ".join(all_tags)
        if len(tags_string) > 1000:
            tags_string = tags_string[:1000] + "... (*truncated*)"

        ratings = {"e": "Explicit", "q": "Questionable/Mature", "s": "Safe"}
        colors = {
            "e": discord.Colour(0xA31014),
            "q": discord.Colour(0xADAA07),
            "s": discord.Colour(0xEB612),
        }
        embed = discord.Embed(colour=colors.get(post.rating))

        embed.set_image(url=post.sample["url"])
        embed.set_thumbnail(url="https://e621.net/apple-touch-icon.png")
        embed.set_author(name=f"Post #{post.id}")

        embed.add_field(
            name="Artist", value=f"`{' '.join(post.tags['artist'])}`", inline=True
        )
        embed.add_field(name="Rating", value=ratings.get(post.rating), inline=True)
        embed.add_field(name="Tags", value=f"`{tags_string}`", inline=False)
        embed.add_field(name="Full Image URL", value=post.file["url"], inline=False)

        return embed

    @cached(cache=LRUCache(maxsize=512))
    async def _cached_search_post(self, pid):
        return await self.client.post(pid)

    @cached(cache=TTLCache(maxsize=512, ttl=1800))
    async def _cached_search_query(self, tags=None, limit=None, page=None):
        return await self.client.posts(tags, limit=limit, page=page)

    @commands.command()
    @commands.check(checks.is_nsfw)
    @commands.cooldown(20, 60, commands.BucketType.guild)
    async def e621(self, ctx, *, tags):
        """Pulls random post from e621 with given tags."""
        if "order:score_asc" in tags:
            await ctx.send("Nope.")
            return
        if "score:" not in tags:
            tags += " score:>25"

        posts = await self._cached_search_query(tags, limit=320)
        if not posts:
            return await ctx.send("No results found!")

        picked = random.choice(posts)
        while self._is_deleted(picked):
            picked = random.choice(posts)
        await ctx.send(embed=self._generate_esix_embed(picked))

    @commands.command()
    @commands.cooldown(20, 60, commands.BucketType.guild)
    async def e926(self, ctx, *, tags):
        """Pulls random post from e926 with given tags."""
        if "order:score_asc" in tags:
            await ctx.send("Nope.")
            return

        tags = tags.replace("rating:e", "").replace("rating:q", "")
        if "score:" not in tags:
            tags += " score:>25"
        if "rating:" not in tags:
            tags += " rating:s"

        posts = await self._cached_search_query(tags, limit=320)
        if not posts:
            return await ctx.send("No results found!")

        picked = random.choice(posts)
        while self._is_deleted(picked):
            picked = random.choice(posts)
        await ctx.send(embed=self._generate_esix_embed(picked))

    @commands.command()
    @commands.cooldown(20, 60, commands.BucketType.guild)
    async def random(self, ctx):
        """Gets random result from e621.
        If channel is not marked with nsfw, rating will always be safe."""
        query = "score:>25"
        if not await checks.is_nsfw(ctx):
            query += " rating:s"

        posts = await self._cached_search_query(
            query, limit=320, page=random.randint(1, 301)
        )
        if not posts:
            return await ctx.send("Somehow I can't get anything from esix...")

        picked = random.choice(posts)
        while self._is_deleted(picked):
            picked = random.choice(posts)
        await ctx.send(embed=self._generate_esix_embed(picked))

    @commands.command()
    @commands.cooldown(30, 60, commands.BucketType.guild)
    async def show(self, ctx, post: str):
        """Shows a post from given URL/ID"""
        if not post.isdigit():
            re_result = re_esix.search(post)
            if not re_result:
                return await ctx.send("Send URL or Post ID!")
            post = re_result[1]

        try:
            picked = await self._cached_search_post(post)
        except BaseException:
            return await ctx.send("Either not found or server got toasted.")
        if not picked:
            return await ctx.send("Post doesn't exist!")
        await ctx.send(embed=self._generate_esix_embed(picked))


def setup(bot):
    bot.add_cog(Furry(bot))
