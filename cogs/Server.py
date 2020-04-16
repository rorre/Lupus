import discord
from discord.ext import commands

class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx):
        return ctx.guild is not None

    @commands.command(name="user")
    async def userinfo(self, ctx, member: discord.Member):
        """Show info about pinged user."""
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

        if member.avatar_url:
            embed.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name="server")
    async def serverinfo(self, ctx):
        """Show info about current server."""
        guild = ctx.guild
        owner = guild.owner.mention if guild.owner else ""
        desc = f"**ID**: `{guild.id}`\r" \
            + f"**Creation date**: `{guild.created_at.isoformat(' ')}`\r" \
            + f"**Region**: `{guild.region}`\r" \
            + f"**Owner**: {owner}\r" \
            + f"**Max presences**: `{guild.max_presences}`\r" \
            + f"**Max member**: `{guild.max_members}`\r" \
            + f"**Custom emojis**: `{len(guild.emojis)}`\r" \
            + f"**Emoji limit**: `{guild.emoji_limit}`\r" \
            + f"**Bitrate limit**: `{int(guild.bitrate_limit/1000)}`kbps\r" \
            + f"**File size limit**: `{round(guild.filesize_limit/1000000, 2)}MB`\r"
        
        embed = discord.Embed(
            title=f"Server info for {guild.name}",
            colour=discord.Colour(0x166fd1),
            description=desc
        )
        if guild.icon_url:
            embed.set_thumbnail(url=str(guild.icon_url))
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Server(bot))
