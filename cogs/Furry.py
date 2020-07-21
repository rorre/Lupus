import mimetypes
import random
import re

import discord
from discord.ext import commands

from helper import checks
from helper.caching import cache
from yippi import AsyncYippiClient

ESIX_REGEX = r"https:\/\/[www\.]*e[(?:621)(?:926)]+\.net\/posts\/(\d+)"
re_esix = re.compile(ESIX_REGEX)


class Furry(commands.Cog):
    blacklist = ['loli', 'foalcon', 'fillies', 'fillycon', 'paedophilia', 'lolicon', 'preteen', 'colt', 'puppy', 'underage', 'pedophilia', 'pups', 'foal', 'kittens', 'filly', 'kemoshota', 'littlefur', 'shota', 'kidfur', 'children', 'duckling', 'puppies', 'kids', 'cubs', 'shotacon', 'kid', 'hatchling', 'young_human', 'fawn', 'kitten']

    def __init__(self, bot):
        self.bot = bot
        self.client = AsyncYippiClient("Lupus", "1.0", "Error-", loop=self.bot.loop, session=self.bot.aiohttp_session)

    def _is_deleted_or_blacklisted(self, post):
        all_tags = []
        for k in post.tags:
            tags_category = post.tags[k]
            for tag in tags_category:
                all_tags.append(tag)

        return post.flags["deleted"] or any([x in all_tags for x in self.blacklist])

    def _generate_esix_embed(self, post):
        all_tags = []
        for k in post.tags:
            tags_category = post.tags[k]
            for tag in tags_category:
                all_tags.append(tag)
        tags_string = " ".join(all_tags)

        post_url = post.sample["url"]
        if not post_url:
            return discord.Embed(
                title="Error",
                colour=discord.Colour(0x4A90E2),
                description="I got a deleted/invalid post from e621. Please try again.",
            )

        if len(tags_string) > 1000:
            tags_string = tags_string[:1000] + "... (*truncated*)"

        ratings = {"e": "Explicit", "q": "Questionable/Mature", "s": "Safe"}
        colors = {
            "e": discord.Colour(0xA31014),
            "q": discord.Colour(0xADAA07),
            "s": discord.Colour(0xEB612),
        }
        embed = discord.Embed(colour=colors.get(post.rating.value))

        mimetype = mimetypes.guess_type(post_url.split("/")[-1])[0]
        if mimetype and mimetype.startswith("image"):
            embed.set_image(url=post_url)
        embed.set_thumbnail(url="https://e621.net/apple-touch-icon.png")
        embed.set_author(name=f"Post #{post.id}")

        embed.add_field(
            name="Artist", value=f"`{' '.join(post.tags['artist'])}`", inline=True
        )
        embed.add_field(name="Rating", value=ratings.get(post.rating.value), inline=True)
        embed.add_field(name="Tags", value=f"`{tags_string}`", inline=False)
        embed.add_field(name="Full URL", value=post.file["url"], inline=False)

        return embed

    async def _cached_search_post(self, pid):
        post = await cache.get(f"post-{pid}")
        if not post:
            post = await self.client.post(pid)
            post._client = None
            await cache.set(f"post-{pid}", post, ttl=1800)
        return post

    async def _cached_search_query(self, tags=None, limit=None, page=None):
        posts = await cache.get(f"search-{tags}")
        if not posts:
            posts = await self.client.posts(tags, limit=limit, page=page)
            if posts:
                for p in posts:
                   p._client = None
                await cache.set(f"search-{tags}", posts, ttl=1800)
        return posts

    @commands.command()
    @commands.check(checks.is_nsfw)
    @commands.cooldown(20, 60, commands.BucketType.guild)
    async def e621(self, ctx, *, tags):
        """Pulls random post from e621 with given tags."""
        if "order:score_asc" in tags or any([x in tags for x in self.blacklist]):
            await ctx.send("Nope.")
            return
        if "status:" in tags and "status:active" not in tags:
            return await ctx.send("Nope.")
        tags += " status:active"
        if "score:" not in tags:
            tags += " score:>25"

        posts = await self._cached_search_query(tags, limit=320)
        if not posts:
            return await ctx.send("No results found!")

        picked = random.choice(posts)
        while self._is_deleted_or_blacklisted(picked):
            picked = random.choice(posts)
        await ctx.send(embed=self._generate_esix_embed(picked))

    @commands.command()
    @commands.cooldown(20, 60, commands.BucketType.guild)
    async def e926(self, ctx, *, tags):
        """Pulls random post from e926 with given tags."""
        if "order:score_asc" in tags or any([x in tags for x in self.blacklist]):
            await ctx.send("Nope.")
            return
        if "status:" in tags and "status:active" not in tags:
            return await ctx.send("Nope.")

        tags = tags.replace("rating:e", "").replace("rating:q", "")
        tags += " status:active"
        if "score:" not in tags:
            tags += " score:>25"
        if "rating:" not in tags:
            tags += " rating:s"

        posts = await self._cached_search_query(tags, limit=320)
        if not posts:
            return await ctx.send("No results found!")

        picked = random.choice(posts)
        while self._is_deleted_or_blacklisted(picked):
            picked = random.choice(posts)
        await ctx.send(embed=self._generate_esix_embed(picked))

    @commands.command()
    @commands.cooldown(20, 60, commands.BucketType.guild)
    async def random(self, ctx):
        """Gets random result from e621.
        If channel is not marked with nsfw, rating will always be safe."""
        query = "score:>25 status:active"
        if not await checks.is_nsfw(ctx):
            query += " rating:s"

        posts = await self._cached_search_query(
            query, limit=320, page=random.randint(1, 301)
        )
        if not posts:
            return await ctx.send("Somehow I can't get anything from esix...")

        picked = random.choice(posts)
        while self._is_deleted_or_blacklisted(picked):
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
        if picked.rating.value != "s" and not checks.is_nsfw(ctx):
            return await ctx.send("Can only send NSFW on NSFW channels.")
        await ctx.send(embed=self._generate_esix_embed(picked))


def setup(bot):
    bot.add_cog(Furry(bot))
