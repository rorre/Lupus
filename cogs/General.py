from datetime import datetime

import discord
from discord.ext import commands

import config
from apis.OpenWeatherMap import OWMClient, OWMException, RateLimitedException
from apis.Urbandictionary import UrbanClient


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.urban_client = UrbanClient(self.bot.aiohttp_session, self.bot.loop)
        self.owm_client = OWMClient(
            config.owm_key, session=self.bot.aiohttp_session, loop=self.bot.loop
        )

    @commands.command(pass_context=True)
    async def avatar(self, ctx, users: commands.Greedy[discord.User]):
        """Sends avatar link of mentioned users."""
        res = "Avatar URL for:\r"
        for user in users:
            res += f"- {user.name}: {user.avatar_url_as(format='png')}\r"
        await ctx.send(res)

    @commands.command(pass_context=True)
    @commands.cooldown(30, 60, commands.BucketType.guild)
    async def urban(self, ctx, *, query):
        """Search Urbandictionary for a definition."""
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
            text="👍 " + str(best.thumbs_up) + " | " + "👎 " + str(best.thumbs_down)
        )
        await ctx.send(embed=embed)

    def _generate_weather_embed(self, w):
        weather = w.weather[0]
        embed = discord.Embed(
            title=f"Weather for {w.name}, {w.sys['country']} :flag_{w.sys['country'].lower()}:",
            colour=discord.Colour(0x6DA1F8),
            description=f"**{weather['main']}** ({weather['description']})\r\n**Temperature**: {w.main['temp']}°C (Feels like {w.main['feels_like']}°)\r\n**Humidity**: {w.main['humidity']}%",
            timestamp=datetime.utcfromtimestamp(w.dt),
        )

        embed.set_thumbnail(
            url=f"http://openweathermap.org/img/wn/{weather['icon']}@2x.png"
        )
        embed.set_footer(
            text="Gathered from OpenWeatherMap",
            icon_url="https://openweathermap.org/themes/openweathermap/assets/vendor/owm/img/icons/logo_60x60.png",
        )

        embed.add_field(name="Wind", value=f"{w.wind['speed']} m/s, ({w.wind['deg']})")
        embed.add_field(
            name="Sunrise",
            value=datetime.fromtimestamp(w.sys["sunrise"]).isoformat(" "),
            inline=True,
        )
        embed.add_field(
            name="Sunset",
            value=datetime.fromtimestamp(w.sys["sunset"]).isoformat(" "),
            inline=True,
        )

        return embed

    @commands.command()
    @commands.cooldown(10, 60, commands.BucketType.guild)
    async def weather(self, ctx, place, state=None, country=None):
        """Sends weather info of a location."""
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

    @commands.command()
    async def inspire(self, ctx):
        """Gets inspiration from InspiroBot."""
        async with self.bot.aiohttp_session.get(self.INSPIROBOT_URL) as res:
            if res.status != 200:
                return await ctx.send("No response from inspirobot.")
            return await ctx.send(await res.text())


def setup(bot):
    bot.add_cog(General(bot))
