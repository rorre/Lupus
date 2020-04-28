import discord
from discord.ext import commands
from jikanpy import AioJikan

from apis.NekosLife import NekoClient


class Weeb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.neko_client = NekoClient(self.bot.aiohttp_session, self.bot.loop)
        self.jikan = AioJikan(session=self.bot.aiohttp_session, loop=self.bot.loop)

    def _create_embed(self, url):
        embed = discord.Embed(colour=discord.Colour(0x4A90E2))
        embed.set_image(url=url)
        embed.set_footer(text="Powered by https://nekos.life/")
        return embed

    async def _doit(self, ctx, user, me_msg, author_msg, action):
        if any(u == ctx.me for u in user):
            msg = me_msg
        elif any(u == ctx.author for u in user):
            msg = author_msg
        else:
            msg = f"{ctx.author.name} {action}s {', '.join(u.name for u in user)}!"

        response = (await self.neko_client.get(action)).get("url")
        if not response:
            return await ctx.send("No response from API.")
        await ctx.send(msg, embed=self._create_embed(response))

    def _create_mal_embed(self, res, manga=False):
        embed = discord.Embed(
            title=res["title"],
            colour=discord.Colour(0x4A90E2),
            url=res["url"],
            description=res.get("synopsis", "No synopsis."),
        )

        if res["image_url"]:
            embed.set_thumbnail(url=res["image_url"])
        embed.set_footer(text="Data taken from MAL by Jikan.moe.")

        embed.add_field(name="Type", value=res["type"], inline=True)
        embed.add_field(name="Score", value=str(res["score"]), inline=True)

        if not manga:
            embed.add_field(name="Rating", value=res["rating"], inline=True)

        embed.add_field(name="Status", value=res["status"], inline=True)
        if manga:
            embed.add_field(
                name="Date Publishing", value=res["published"]["string"], inline=True
            )
        else:
            embed.add_field(
                name="Date Airing", value=res["aired"]["string"], inline=True
            )

        if manga:
            embed.add_field(name="Volumes", value=str(res["volumes"]), inline=True)
            embed.add_field(name="Chapters", value=str(res["chapters"]), inline=True)
        else:
            embed.add_field(name="Episodes", value=str(res["episodes"]), inline=True)
            embed.add_field(name="Season", value=res["premiered"], inline=True)
            embed.add_field(
                name="Opening Theme",
                value="\r\n".join(res["opening_themes"]),
                inline=False,
            )
            embed.add_field(
                name="Ending Theme",
                value="\r\n".join(res["ending_themes"]),
                inline=False,
            )

        return embed

    def _create_mal_search_embed(self, res, manga=False):
        if not res:
            desc = ":information_source: **No result found.**"
        else:
            desc = ""
            for i, item in enumerate(res):
                desc += (
                    f"**{i+1}. [{item['title']}]({item['url']})**\r\n"
                    + f"MAL ID: {item['mal_id']}\r\n"
                    + f"Synopsis: {item.get('synopsis', 'No synopsis available.')[:100]}...\r\n"
                    + f"Type: {item['type']}\r\n"
                    + f"Score: {item['score']}\r\n"
                )
                if not manga:
                    desc += f"Rating: {item['rated']}\r\n"
                desc += "\r\n"

        embed = discord.Embed(
            title="Search result", colour=discord.Colour(0x4A90E2), description=desc
        )
        embed.set_footer(text="Data taken from MAL by Jikan.moe.")

        return embed

    @commands.command()
    @commands.cooldown(10, 20, commands.BucketType.guild)
    async def neko(self, ctx):
        """Gets random neko image."""
        response = (await self.neko_client.get("neko")).get("url")
        if not response:
            return await ctx.send("No response from API.")
        await ctx.send(embed=self._create_embed(response))

    @commands.command()
    @commands.cooldown(10, 20, commands.BucketType.guild)
    async def cat(self, ctx):
        """Gets random cat image."""
        response = (await self.neko_client.get("meow")).get("url")
        if not response:
            return await ctx.send("No response from API.")
        await ctx.send(embed=self._create_embed(response))

    @commands.command()
    @commands.cooldown(10, 20, commands.BucketType.guild)
    async def tickle(self, ctx, user: commands.Greedy[discord.Member]):
        """Tickles other user."""
        await self._doit(
            ctx, user, "Hey! It tickles!", "Can you really tickle yourself?", "tickle"
        )

    @commands.command()
    @commands.cooldown(10, 20, commands.BucketType.guild)
    async def poke(self, ctx, user: commands.Greedy[discord.Member]):
        """Pokes other user."""
        await self._doit(
            ctx, user, "Quit poking!", f"{ctx.author.name} pokes theirselves.", "poke"
        )

    @commands.command()
    @commands.cooldown(10, 20, commands.BucketType.guild)
    async def kiss(self, ctx, user: commands.Greedy[discord.Member]):
        """Kisses other user."""
        await self._doit(ctx, user, "😳", "Self-love I see.", "kiss")

    @commands.command()
    @commands.cooldown(10, 20, commands.BucketType.guild)
    async def slap(self, ctx, user: commands.Greedy[discord.Member]):
        """Slaps other user."""
        await self._doit(
            ctx, user, "Ow!", f"{ctx.author.name} slaps theirselves.", "slap"
        )

    @commands.command()
    @commands.cooldown(10, 20, commands.BucketType.guild)
    async def cuddle(self, ctx, user: commands.Greedy[discord.Member]):
        """Cuddles other user."""
        await self._doit(
            ctx, user, "Cuddles!", f"{ctx.author.name} cuddles theirselves.", "cuddle"
        )

    @commands.command()
    @commands.cooldown(10, 20, commands.BucketType.guild)
    async def hug(self, ctx, user: commands.Greedy[discord.Member]):
        """Hugs other user."""
        await self._doit(
            ctx, user, "Hugs!", f"{ctx.author.name} hugs theirselves.", "hug"
        )

    @commands.command()
    @commands.cooldown(10, 20, commands.BucketType.guild)
    async def pat(self, ctx, user: commands.Greedy[discord.Member]):
        """Pats other user."""
        await self._doit(
            ctx, user, "UwU", f"{ctx.author.name} pats theirselves.", "pat"
        )

    @commands.command()
    @commands.cooldown(5, 30, commands.BucketType.guild)
    async def anime(self, ctx, id):
        """Lookup MAL for an anime based on its MAL ID."""
        try:
            res = await self.jikan.anime(id)
        except Exception as e:
            return await ctx.send(str(e))
        await ctx.send(embed=self._create_mal_embed(res))

    @commands.command()
    @commands.cooldown(5, 30, commands.BucketType.guild)
    async def manga(self, ctx, id):
        """Lookup MAL for a manga based on its MAL ID."""
        try:
            res = await self.jikan.manga(id)
        except Exception as e:
            return await ctx.send(str(e))
        await ctx.send(embed=self._create_mal_embed(res, manga=True))

    @commands.command()
    @commands.cooldown(10, 60, commands.BucketType.guild)
    async def search_anime(self, ctx, query):
        """Searches MAL for animes with given query."""
        try:
            res = await self.jikan.search("anime", query, parameters={"limit": 8})
        except Exception as e:
            return await ctx.send(str(e))
        await ctx.send(embed=self._create_mal_search_embed(res["results"]))

    @commands.command()
    @commands.cooldown(10, 60, commands.BucketType.guild)
    async def search_manga(self, ctx, query):
        """Searches MAL for mangas with given query."""
        try:
            res = await self.jikan.search("manga", query, parameters={"limit": 8})
        except Exception as e:
            return await ctx.send(str(e))
        await ctx.send(embed=self._create_mal_search_embed(res["results"], manga=True))


def setup(bot):
    bot.add_cog(Weeb(bot))
