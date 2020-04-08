import random
import discord
from discord.ext import commands
from apis import UrbanClient
from PIL import Image
import string
import os
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial

class General(commands.Cog):
    """General/fun stuffs.

    Commands:
        about      Well uhh, the bot's info, of course...
        anime      Searches anime to MAL
        avatar     Sends avatar link of mentioned user.
        choose     Choose one of a lot arguments
        manga      Searches manga to MAL
        report     Reports a problem to bot owner.
        sauce      Reverse search an image given
        urban      Searches urbandictionary for a definition.
        forecast   Sends forecast of a location
        weather    Sends weather of a location"""

    def __init__(self, bot):
        self.bot = bot
        self.urban_client = UrbanClient(self.bot.aiohttp_session, self.bot.loop)
        self.thread_pool = ThreadPoolExecutor()
    
    def _generate_random_name(self, n):
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))
    
    def _process_image(self, name):
        Image.open("tmp/" + name).save("tmp/more-" + name, 'JPEG', quality=1)

    @commands.command(pass_context=True)
    async def avatar(self, ctx, message):
        """Sends avatar link of mentioned users.
        Arguments:
        `(mentioned users)` : `discord.User`"""
        for user in ctx.message.mentions:
            await ctx.send(f"""Avatar URL for {user.name}: {user.avatar_url}""")
    
    @commands.command(pass_context=True)
    async def urban(self, ctx, *, query):
        results = await self.urban_client.search_term(query)
        if not results:
            return await ctx.send("No results found!")
        best = results[0]

        if len(best.definition) > 1024:
            best.definition = best.definition[:1000] + "... *(truncated)*"
        if len(best.example) > 1024:
            best.example = best.example[:1000] + "... *(truncated)*"

        embed = discord.Embed(title=f"**{best.word}**", url=best.permalink, description=f"by: {best.author}", color=0xc4423c)
        embed.add_field(name="Definition", value=best.definition, inline=False)
        embed.add_field(name="Example", value=best.example, inline=True)
        embed.set_footer(text=u"👍 " + str(best.thumbs_up) + " | " + u"👎 " + str(best.thumbs_down))
        await ctx.send(embed=embed)
    
    @commands.command()
    async def about(self, ctx):
        """Well uhh, the bot's info, of course..."""
        embed = discord.Embed(colour=discord.Colour(0x4a90e2))

        embed.add_field(name="Author", value="-Keitaro/rorre/Error- // [Github](https://github.com/rorre) // [Twitter](https://twitter.com/osuRen_)", inline=False)
        embed.add_field(name="Library", value="Discord.py", inline=False)
        embed.add_field(name="Repository", value="[https://github.com/rorre/Furbot](https://github.com/rorre/Furbot)", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def choose(self, ctx, *, args):
        """Choose one of a lot arguments

        Arguments:
        `*args` : list  
        The message but its splitted to a list.

        Usage:
        `f!choose arg1 | arg2 | arg3 | ...`"""
        choices = args.split('|')
        for i in range(len(choices)):
            if not choices[i].strip():
                return await ctx.send(f"Argument number {i+1} is invalid.")
        if len(choices) < 2:
            await ctx.send("You need to send at least 2 arguments!")
            return
        await ctx.send(random.choice(choices).strip() + ", of course!")

    @commands.command()
    async def jpeg(self, ctx):
        """Basically needsmorejpeg

        Usage: Send an image wiyh f!jpeg as description"""
        embeds = ctx.message.attachments
        images = []
        filenames = []

        if not os.path.exists("tmp"):
            os.makedirs("tmp")
        
        if not embeds:
            await ctx.send("Please send me an image with `f!jpeg` as description!")
        
        for embed in embeds:
            name = self._generate_random_name(10) + ".jpg"
            await embed.save("tmp/" + name)

            await self.bot.loop.run_in_executor(
                self.thread_pool,
                partial(self._process_image, name)
            )

            filenames.append("tmp/more-" + name)
            filenames.append("tmp/" + name)
            images.append(discord.File("tmp/more-" + name))
        await ctx.send("Done!", files=images)

        try:
            for fil in filenames:
                os.remove(fil)
        except:
            pass

def setup(bot):
    bot.add_cog(General(bot))