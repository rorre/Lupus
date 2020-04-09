import random
import discord
from discord.ext import commands
from apis.Urbandictionary import UrbanClient
from apis.OpenWeatherMap import OWMClient, RateLimitedException, OWMException
from PIL import Image
import string
import os
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial
import config
from datetime import datetime


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
        self.urban_client = UrbanClient(
            self.bot.aiohttp_session, self.bot.loop)
        self.owm_client = OWMClient(
            config.owm_key, session=self.bot.aiohttp_session, loop=self.bot.loop)
        self.thread_pool = ThreadPoolExecutor()

    def _generate_random_name(self, n):
        return "".join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits)
            for _ in range(n)
        )

    def _process_image(self, name):
        Image.open("tmp/" + name).save("tmp/more-" + name, "JPEG", quality=1)

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

        embed = discord.Embed(
            title=f"**{best.word}**",
            url=best.permalink,
            description=f"by: {best.author}",
            color=0xC4423C,
        )
        embed.add_field(name="Definition", value=best.definition, inline=False)
        embed.add_field(name="Example", value=best.example, inline=True)
        embed.set_footer(
            text="👍 " + str(best.thumbs_up) + " | " +
            "👎 " + str(best.thumbs_down)
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def about(self, ctx):
        """Well uhh, the bot's info, of course..."""
        embed = discord.Embed(colour=discord.Colour(0x4A90E2))

        embed.add_field(
            name="Author",
            value="-Keitaro/rorre/Error- // [Github](https://github.com/rorre) // [Twitter](https://twitter.com/osuRen_)",
            inline=False,
        )
        embed.add_field(name="Library", value="Discord.py", inline=False)
        embed.add_field(
            name="Repository",
            value="[https://github.com/rorre/Furbot](https://github.com/rorre/Furbot)",
            inline=False,
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def choose(self, ctx, *, args):
        """Choose one of a lot arguments

        Arguments:
        `*args` : list  
        The message but its splitted to a list.

        Usage:
        `f!choose arg1 | arg2 | arg3 | ...`"""
        choices = args.split("|")
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
                self.thread_pool, partial(self._process_image, name)
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

    def _generate_weather_embed(self, w):
        weather = w.weather[0]
        embed = discord.Embed(title=f"Weather for {w.name}, {w.sys['country']} :flag_{w.sys['country'].lower()}:", colour=discord.Colour(
            0x6da1f8), description=f"**{weather['main']}** ({weather['description']})\r\n**Temperature**: {w.main['temp']}°C (Feels like {w.main['feels_like']}°)\r\n**Humidity**: {w.main['humidity']}%", timestamp=datetime.utcfromtimestamp(w.dt))

        embed.set_thumbnail(
            url=f"http://openweathermap.org/img/wn/{weather['icon']}@2x.png")
        embed.set_footer(text="Gathered from OpenWeatherMap",
                         icon_url="https://openweathermap.org/themes/openweathermap/assets/vendor/owm/img/icons/logo_60x60.png")

        embed.add_field(
            name="Wind", value=f"{w.wind['speed']} m/s, ({w.wind['deg']})")
        embed.add_field(name="Sunrise", value=datetime.fromtimestamp(
            w.sys['sunrise']).isoformat(" "), inline=True)
        embed.add_field(name="Sunset", value=datetime.fromtimestamp(
            w.sys['sunset']).isoformat(" "), inline=True)

        return embed

    @commands.command()
    async def weather(self, ctx, place, state=None, country=None):
        """Sends weather info of a location

        Usage: f!weather <place> [(<state>) <country code>]
        Anything in brackets are optional. But recommended for more accurate result."""
        if state:
            place += "," + state
        if country:
            place += "," + country
        try:
            weather = await self.owm_client.get_weather(place)
        except RateLimitedException:
            return await ctx.send("Bot got rate limited by server, sorry.")
        except OWMException as e:
            return await ctx.send(str(e))
        await ctx.send(embed=self._generate_weather_embed(weather))


def setup(bot):
    bot.add_cog(General(bot))
