import discord


async def is_nsfw(ctx):
    if not isinstance(ctx.channel, discord.DMChannel) and not isinstance(
        ctx.channel, discord.GroupChannel
    ):
        return ctx.channel.is_nsfw()
    return True


async def is_owner(ctx):
    appinfo = await ctx.bot.application_info()
    return ctx.author.id == appinfo.owner.id
