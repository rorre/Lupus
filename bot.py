import sys
import traceback

import aiohttp
from discord.ext import commands

cogs = ["cogs.Furry", "cogs.General"]


class FurBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or("f!"), **kwargs)
        self.aiohttp_session = aiohttp.ClientSession(loop=self.loop)
        for cog in cogs:
            try:
                self.load_extension(cog)
            except Exception as exc:
                print(
                    "Could not load extension {0} due to {1.__class__.__name__}: {1}".format(
                        cog, exc
                    )
                )

    async def find_channel(self, guild):
        """Automatically find suitable channel to send, this is invoked for `on_guild_join(guild)`"""
        for c in guild.text_channels:
            if not c.permissions_for(guild.me).send_messages:
                continue
            return c

    async def on_guild_join(self, guild):
        """Sends greeting message to server when joining, but it searches for suitable channel first by invoking `find_channel(guild)`"""
        channel = await self.find_channel(guild)
        await channel.send(
            "Hello there, "
            + guild.name
            + """!\r
    I'm FurBot! If you want to try me out, go ahead check out the help! The command is `f!help`.\r\r
    Thank you very much for using this bot!"""
        )

    async def on_command_error(self, ctx, error):
        ignored = (commands.CommandNotFound, commands.CheckFailure)
        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return
        elif isinstance(error, commands.UserInputError):
            return await ctx.send_help(entity=ctx.command)
        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f"Rate limited. Try again in `{error.retry_after}` seconds.")
        elif isinstance(error, commands.CommandInvokeError):
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )
            return await ctx.send(
                "An exception has occured: `{}` on command `{}`".format(error.__class__.__name__,ctx.command.name)
            )


bot = FurBot()
if __name__ == "__main__":
    import config
    token = config.token
    bot.run(token)
