import discord
from discord.ext import commands

class Server(commands.Cog):
    """Server-only commands.

    Commands:
    """
    def __init__(self, bot):
        self.bot = bot
    
    @Server.cog_check
    async def server_only(self, ctx):
        return ctx.guild is not None

    @commands.command()
    async def userinfo(self, ctx, member: discord.Member):
        role_str = []
        for role in member.roles:
            role_str.append(role.name)
        is_boost = member.premium_since
        if is_boost:
            boost_str = is_boost.isoformat(' ')
        else:
            boost_str = "Not boosting."
        desc = f"**ID**: `{member.id}`\r\n" \
               + f"**Bot**: `{member.bot}`\r\n" \
               + f"**Creation date**: `{member.created_at.isoformat(' ')}`\r\n" \
               + f"**Display name**: `{member.display_name}`\r\n" \
               + f"**Roles**: `{' '.join(role_str)}`" \
               + f"**Boosting since**: {boost_str}"
        
        embed = discord.Embed(
            title="User info for -Keitaro",
            colour=discord.Colour(0x166fd1),
            description=desc
        )
        embed.set_thumbnail(url=member.avatar_url)

    @commands.command()
    async def serverinfo(self, ctx):
        pass

    