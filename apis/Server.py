import discord
from discord.ext import commands

class Server(commands.Cog):
    """Server-only commands.

    Commands:
    """
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def user(self, ctx, *, member: discord.Member):
        pass

    @commands.command()
    async def server(self, ctx):
        pass

    