import random
import discord
from discord.ext import commands
from typing import Optional
from datetime import datetime
import asyncio

class Server(commands.Cog, name="Server Only"):
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx):
        return ctx.guild is not None

    def _generate_user_details(self, member):
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
               + f"**Roles**: `{', '.join(role_str)}`\r\n" \
               + f"**Boosting since**: {boost_str}"

        return desc

    @commands.command(name="user")
    async def userinfo(self, ctx, member: discord.Member):
        """Show info about pinged user."""
        desc = self._generate_user_details(member)
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

    @commands.command()
    async def someone(self, ctx, requires_role : Optional[discord.Role] = None, *message):
        """Picks someone from list of members with extra message.
        'requires_role' is to filter the members. That means only members with mentioned role can get picked.
        'message' is the extra message to input after the user."""
        guild_members = ctx.guild.members
        if requires_role:
            members = list(filter(lambda x: requires_role in x.roles, guild_members))
        else:
            members = guild_members
        member = random.choice(members)
        message = ' '.join(message)
        await ctx.send(f"{member.display_name} {message}")
    
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, members : commands.Greedy[discord.Member], *, reason="No reason provided."):
        if not ctx.channel.permissions_for(ctx.me).kick_members:
            return await ctx.send("I don't have permissions to kick members!")
        if len(members) == 0:
            return await ctx.send_help(ctx.command)

        new = []
        for m in members:
            if any(x.id == m.id for x in new): continue
            new.append(m)
        
        members = new
        if len(members) > 4:
            return await ctx.send("Sorry, I can only kick 4 members at a time!")
        embeds = []
        current_time = datetime.now()
        for member in members:
            desc = self._generate_user_details(member)
            embed = discord.Embed(title="Kick Member", colour=discord.Colour(0xce1e24), description=desc, timestamp=current_time)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            embed.add_field(name="Reason", value=reason)
            embeds.append(embed)
        msg = await ctx.send("Are you sure you want to kick these members? (Times out in 1 minute.)")
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        embed_messages = []
        for e in embeds:
            embed_messages.append(await ctx.send(embed=e))

        def check(payload):
            return payload.message_id == msg.id \
                and payload.user_id == ctx.author.id
        
        try:
            payload = await self.bot.wait_for('raw_reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await msg.edit(content="Timed out.")
        else:
            if str(payload.emoji) == "❌":
                return await msg.edit(content="Cancelled.")
            for member in members:
                try:
                    await member.kick(reason=reason)
                except discord.Forbidden:
                    await msg.edit(content=f"Cannot kick {member.display_name}.")
            await ctx.send("Done!")
        finally:
            for message in embed_messages:
                await message.delete()


def setup(bot):
    bot.add_cog(Server(bot))
