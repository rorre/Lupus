import discord
from discord.ext import commands

from apis.NekosLife import NekoClient


class Weeb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.neko_client = NekoClient(self.bot.aiohttp_session, self.bot.loop)

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
        await self._doit(ctx, user, "Hey! It tickles!", "Can you really tickle yourself?", "tickle")

    @commands.command()
    @commands.cooldown(10, 20, commands.BucketType.guild)
    async def poke(self, ctx, user: commands.Greedy[discord.Member]):
        """Pokes other user."""
        await self._doit(ctx, user, "Quit poking!", f"{ctx.author.name} pokes theirselves.", "poke")

    @commands.command()
    @commands.cooldown(10, 20, commands.BucketType.guild)
    async def kiss(self, ctx, user: commands.Greedy[discord.Member]):
        """Kisses other user."""
        await self._doit(ctx, user, "😳", "Self-love I see.", "kiss")

    @commands.command()
    @commands.cooldown(10, 20, commands.BucketType.guild)
    async def slap(self, ctx, user: commands.Greedy[discord.Member]):
        """Slaps other user."""
        await self._doit(ctx, user, "Ow!", f"{ctx.author.name} slaps theirselves.", "slap")

    @commands.command()
    @commands.cooldown(10, 20, commands.BucketType.guild)
    async def cuddle(self, ctx, user: commands.Greedy[discord.Member]):
        """Cuddles other user."""
        await self._doit(ctx, user, "Cuddles!", f"{ctx.author.name} cuddles theirselves.", "cuddle")

    @commands.command()
    @commands.cooldown(10, 20, commands.BucketType.guild)
    async def hug(self, ctx, user: commands.Greedy[discord.Member]):
        """Hugs other user."""
        await self._doit(ctx, user, "Hugs!", f"{ctx.author.name} hugs theirselves.", "hug")

    @commands.command()
    @commands.cooldown(10, 20, commands.BucketType.guild)
    async def pat(self, ctx, user: commands.Greedy[discord.Member]):
        """Pats other user."""
        await self._doit(ctx, user, "UwU", f"{ctx.author.name} pats theirselves.", "pat")


def setup(bot):
    bot.add_cog(Weeb(bot))
