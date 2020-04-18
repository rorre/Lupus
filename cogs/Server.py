import argparse
import asyncio
import random
import shlex
from datetime import datetime
from typing import Optional

import discord
from dateutil import parser as date_parser
from discord.ext import commands

parser = argparse.ArgumentParser()
parser.add_argument("--before")
parser.add_argument("--after")
parser.add_argument("--around")


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
            boost_str = is_boost.isoformat(" ")
        else:
            boost_str = "Not boosting."

        desc = (
            f"**ID**: `{member.id}`\r\n"
            + f"**Bot**: `{member.bot}`\r\n"
            + f"**Creation date**: `{member.created_at.isoformat(' ')}`\r\n"
            + f"**Display name**: `{member.display_name}`\r\n"
            + f"**Roles**: `{', '.join(role_str)}`\r\n"
            + f"**Boosting since**: {boost_str}"
        )

        return desc

    @commands.command(name="user")
    async def userinfo(self, ctx, member: discord.Member):
        """Show info about pinged user."""
        desc = self._generate_user_details(member)
        embed = discord.Embed(
            title=f"User info for {member.display_name}",
            colour=discord.Colour(0x166FD1),
            description=desc,
        )

        if member.avatar_url:
            embed.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=embed)

    @commands.command(name="server")
    async def serverinfo(self, ctx):
        """Show info about current server."""
        guild = ctx.guild
        owner = guild.owner.mention if guild.owner else ""
        desc = (
            f"**ID**: `{guild.id}`\r"
            + f"**Creation date**: `{guild.created_at.isoformat(' ')}`\r"
            + f"**Region**: `{guild.region}`\r"
            + f"**Owner**: {owner}\r"
            + f"**Max presences**: `{guild.max_presences}`\r"
            + f"**Max member**: `{guild.max_members}`\r"
            + f"**Custom emojis**: `{len(guild.emojis)}`\r"
            + f"**Emoji limit**: `{guild.emoji_limit}`\r"
            + f"**Bitrate limit**: `{int(guild.bitrate_limit/1000)}`kbps\r"
            + f"**File size limit**: `{round(guild.filesize_limit/1000000, 2)}MB`\r"
        )

        embed = discord.Embed(
            title=f"Server info for {guild.name}",
            colour=discord.Colour(0x166FD1),
            description=desc,
        )
        if guild.icon_url:
            embed.set_thumbnail(url=str(guild.icon_url))

        await ctx.send(embed=embed)

    @commands.command()
    async def someone(
        self, ctx, requires_role: Optional[discord.Role] = None, *message
    ):
        """Picks someone from list of members with extra message.
        'requires_role' is to filter the members. That means only members with mentioned role can get picked.
        'message' is the extra message to input after the user."""
        guild_members = ctx.guild.members
        if requires_role:
            members = list(filter(lambda x: requires_role in x.roles, guild_members))
        else:
            members = guild_members
        member = random.choice(members)
        message = " ".join(message)
        await ctx.send(f"{member.display_name} {message}")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(
        self,
        ctx,
        members: commands.Greedy[discord.Member],
        *,
        reason="No reason provided.",
    ):
        """Kicks member(s)."""
        if len(members) == 0:
            return await ctx.send_help(ctx.command)

        new = []
        for m in members:
            if any(x.id == m.id for x in new):
                continue
            new.append(m)

        members = new
        if len(members) > 4:
            # Prevent discord rate limiting.
            return await ctx.send("Sorry, I can only kick 4 members at a time!")

        embeds = []
        current_time = datetime.utcnow()
        for member in members:
            desc = self._generate_user_details(member)
            embed = discord.Embed(
                title="Kick Member",
                colour=discord.Colour(0xCE1E24),
                description=desc,
                timestamp=current_time,
            )
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.avatar_url
            )
            embed.add_field(name="Reason", value=reason)
            embeds.append(embed)

        msg = await ctx.send(
            "Are you sure you want to kick these members? (Times out in 1 minute.)"
        )
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        embed_messages = []
        for e in embeds:
            embed_messages.append(await ctx.send(embed=e))

        def check(payload):
            return payload.message_id == msg.id and payload.user_id == ctx.author.id

        try:
            payload = await self.bot.wait_for(
                "raw_reaction_add", timeout=60.0, check=check
            )
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

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(
        self,
        ctx,
        members: commands.Greedy[discord.Member],
        *,
        reason="No reason provided.",
        delete_message_days: int = 1,
    ):
        """Bans member(s)."""
        # TODO: Find a way so its not a copy paste of kick command lol
        if len(members) == 0:
            return await ctx.send_help(ctx.command)

        new = []
        for m in members:
            if any(x.id == m.id for x in new):
                continue
            new.append(m)

        members = new
        if len(members) > 4:
            # Prevent discord rate limiting.
            return await ctx.send("Sorry, I can only ban 4 members at a time!")

        embeds = []
        current_time = datetime.utcnow()
        for member in members:
            desc = self._generate_user_details(member)
            embed = discord.Embed(
                title="Ban Member",
                colour=discord.Colour(0xCE1E24),
                description=desc,
                timestamp=current_time,
            )
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.avatar_url
            )
            embed.add_field(name="Reason", value=reason)
            embeds.append(embed)

        msg = await ctx.send(
            "Are you sure you want to ban these members? (Times out in 1 minute.)"
        )
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        embed_messages = []
        for e in embeds:
            embed_messages.append(await ctx.send(embed=e))

        def check(payload):
            return payload.message_id == msg.id and payload.user_id == ctx.author.id

        try:
            payload = await self.bot.wait_for(
                "raw_reaction_add", timeout=60.0, check=check
            )
        except asyncio.TimeoutError:
            await msg.edit(content="Timed out.")
        else:
            if str(payload.emoji) == "❌":
                return await msg.edit(content="Cancelled.")
            for member in members:
                try:
                    await member.ban(
                        reason=reason, delete_message_days=delete_message_days
                    )
                except discord.Forbidden:
                    await msg.edit(content=f"Cannot ban {member.display_name}.")
            await ctx.send("Done!")
        finally:
            for message in embed_messages:
                await message.delete()

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx, n: int, *, args=None):
        """Purge n number of messages.

        There are extra arguments that could be parsed.
        --before <datetime>: Delete messages before this date.
        --after <datetime> : Delete messages after this date.
        --around <datetime>: Delete messages around this date.
        <datetime> will ALWAYS be in UTC."""
        args = args if args else ""  # Prevent shlex from freezing because of None.
        before = None
        after = None
        around = None

        arguments = parser.parse_args(shlex.split(args))
        if arguments.after:
            before = date_parser.parse(arguments.before)
        if arguments.after:
            after = date_parser.parse(arguments.after)
        if arguments.around:
            around = date_parser.parse(arguments.around)

        if n > 500:
            return await ctx.send("Maximum purge is 500 messages.")
        await ctx.send("Purging...")
        await ctx.channel.purge(limit=n, before=before, after=after, around=around)
        await ctx.send(f"Done purging ~{n} messages!")


def setup(bot):
    bot.add_cog(Server(bot))
