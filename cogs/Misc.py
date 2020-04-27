import os
import time

import discord
import psutil
from discord.ext import commands

start_time = time.time()

MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR


def timedelta(start, end):
    delta = int(end - start)

    days = delta // DAY
    delta %= DAY
    hours = delta // HOUR
    delta %= HOUR
    minutes = delta // 60
    delta %= MINUTE
    seconds = delta % 60

    return f"{days}d:{hours}h:{minutes}m:{seconds}s"


class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stats(self, ctx):
        """Current bot stats."""
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / 1024 / 1024
        cpu_usage = process.cpu_percent()

        joined_guilds = len(self.bot.guilds)
        served_users = len(self.bot.users)

        current_time = time.time()
        delta = timedelta(start_time, current_time)

        embed_body = (
            f"**Memory usage**: `{int(memory_usage)}MB`\r"
            + f"**CPU**: `{cpu_usage}%`\r"
            + f"**Joined guilds**: `{joined_guilds}`\r"
            + f"**Users served**: `{served_users}`\r"
            + f"**Uptime**: `{delta}`\r"
        )

        embed = discord.Embed(
            title="Stats", colour=discord.Colour(0x3A79B8), description=embed_body
        )
        embed.set_thumbnail(url=str(self.bot.user.avatar_url))
        await ctx.send(embed=embed)

    @commands.command()
    async def about(self, ctx):
        """Well, the bot's info, of course..."""
        embed = discord.Embed(title="About", colour=discord.Colour(0x4A90E2))
        embed.set_thumbnail(url=str(self.bot.user.avatar_url))
        embed.add_field(
            name="Author",
            value="-Keitaro/rorre/Error- // [Github](https://github.com/rorre) // [Twitter](https://twitter.com/osuRen_)",
            inline=False,
        )
        embed.add_field(name="Library", value="Discord.py", inline=False)
        embed.add_field(
            name="Repository",
            value="[https://git.rorre.xyz/rorre/Furbot](https://git.rorre.xyz/rorre/Furbot)",
            inline=False,
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx):
        """Gets an invite link for the bot."""
        cid = self.bot.appinfo.id
        permissions = discord.Permissions.text()
        permissions.update(
            kick_members=True,
            ban_members=True,
            add_reactions=True,
            manage_messages=True,
        )
        oauth = discord.utils.oauth_url(cid, permissions=permissions)
        desc = (
            "Thank you for your interest in inviting this bot to other server!\r"
            + f"[Invite URL]({oauth})"
        )
        embed = discord.Embed(
            title="Invite", colour=discord.Colour(0x4A90E2), description=desc
        )
        embed.set_thumbnail(url=str(self.bot.user.avatar_url))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
