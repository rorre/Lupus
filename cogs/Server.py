import discord
from discord.ext import commands

class Server(commands.Cog):
    """Server-only commands.

    Commands:
    """
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx):
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
               + f"**Roles**: `{' '.join(role_str)}`\r\n" \
               + f"**Boosting since**: {boost_str}"
        
        embed = discord.Embed(
            title=f"User info for {member.display_name}",
            colour=discord.Colour(0x166fd1),
            description=desc
        )
        embed.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=embed)

    @commands.command()
    async def serverinfo(self, ctx):
        pass

def setup(bot):
    bot.add_cog(Server(bot))
