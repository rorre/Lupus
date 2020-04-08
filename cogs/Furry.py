from yippi import AsyncYippiClient
from helper import checks
from discord.ext import commands
import random
import discord
import re

ESIX_REGEX = r'https:\/\/[www\.]*e[(?:621)(?:926)]+\.net\/posts\/(\d+)'
re_esix = re.compile(ESIX_REGEX)

class Furry(commands.Cog):
    """What every furries need.

    Commands:
        e621       Searches e621 with given queries.
        e926       Searches e926 with given queries.
        randompick Output random result from e621/e926.  
        show       Show a post from e621/e926 with given post ID"""

    def __init__(self, bot):
        self.bot = bot
        self.client = AsyncYippiClient('FurBot', '1.0', 'Error-', loop=self.bot.loop)

    def _generate_esix_embed(self, post):
        all_tags = []
        for k in post.tags:
            tags_category = post.tags[k]
            for tag in tags_category:
                all_tags.append(tag)
        tags_string = ' '.join(all_tags)
        if len(tags_string) > 1000:
            tags_string = tags_string[:1000] + "... (*truncated*)"

        ratings = {
            "e": "Explicit",
            "q": "Questionable/Mature",
            "s": "Safe"
        }

        embed = discord.Embed(colour=discord.Colour(0xa31014))

        embed.set_image(url=post.sample['url'])
        embed.set_thumbnail(url="https://e621.net/apple-touch-icon.png")
        embed.set_author(name=f"Post #{post.id}")

        embed.add_field(name="Artist", value=f"`{' '.join(post.tags['artist'])}`", inline=True)
        embed.add_field(name="Rating", value=ratings.get(post.rating), inline=True)
        embed.add_field(name="Tags", value=f"`{tags_string}`", inline=False)
        embed.add_field(name="Full Image URL", value=post.file['url'], inline=False)

        return embed

    @commands.command()
    @commands.check(checks.is_nsfw)
    async def e621(self, ctx, *, tags):
        if "order:score_asc" in tags:
            await ctx.send("Nope.")
            return
        if 'score:' not in tags:
            tags += " score:>25"
        posts = await self.client.posts(tags, limit=320)
        if not posts:
            return await ctx.send("No results found!")
        picked = random.choice(posts)
        await ctx.send(embed=self._generate_esix_embed(picked))

    @commands.command()
    async def e926(self, ctx, *, tags):
        if "order:score_asc" in tags:
            await ctx.send("Nope.")
            return
        tags = tags.replace("rating:e", "").replace("rating:q", "")
        if 'score:' not in tags:
            tags += " score:>25"
        if 'rating:' not in tags:
            tags += " rating:s"
        posts = await self.client.posts(tags, limit=320)
        if not posts:
            return await ctx.send("No results found!")
        picked = random.choice(posts)
        await ctx.send(embed=self._generate_esix_embed(picked))
    
    @commands.command()
    async def randompick(self, ctx):
        query = "score:>25"
        if not checks.is_nsfw(ctx):
            query += " rating:s"
        posts = await self.client.posts(query, limit=320, page=random.randint(1,301))
        if not posts:
            return await ctx.send("Somehow I can't get anything from esix...")
        picked = random.choice(posts)
        await ctx.send(embed=self._generate_esix_embed(picked))
    
    @commands.command()
    async def show(self, ctx, post: str):
        if not post.isdigit():
            re_result = re_esix.search(post)
            if not re_result:
                return await ctx.send("Send URL or Post ID!")
            post = re_result[1]
        try:
            picked = await self.client.post(post)
        except:
            return await ctx.send("Either not found or server got toasted.")
        if not picked:
            return await ctx.send("Post doesn't exist!")
        await ctx.send(embed=self._generate_esix_embed(picked))

def setup(bot):
    bot.add_cog(Furry(bot))