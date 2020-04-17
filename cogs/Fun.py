import os
import random
import string
import typing
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial

import discord
from discord.ext import commands

from PIL import Image


class Fun(commands.Cog):
    INSPIROBOT_URL = "https://inspirobot.me/api?generate=true"

    def __init__(self, bot):
        self.bot = bot
        self.thread_pool = ThreadPoolExecutor()

    def _generate_random_name(self, n):
        return "".join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits)
            for _ in range(n)
        )

    def _process_image(self, name):
        Image.open("tmp/" + name).save("tmp/more-" + name, "JPEG", quality=1)

    @commands.command()
    @commands.cooldown(10, 60, commands.BucketType.guild)
    async def jpeg(self, ctx):
        """Basically needsmorejpeg.
        Usage: Send an image wiyh f!jpeg as description"""
        attachments = ctx.message.attachments
        images = []
        filenames = []

        if not os.path.exists("tmp"):
            os.makedirs("tmp")

        if not attachments:
            return await ctx.send(
                "Please send me an image with `f!jpeg` as description!"
            )

        for attachment in attachments:
            if attachment.filename.split(".")[-1] not in ("jpg", "png"):
                continue
            name = self._generate_random_name(10) + ".jpg"
            await attachment.save("tmp/" + name)

            await self.bot.loop.run_in_executor(
                self.thread_pool, partial(self._process_image, name)
            )

            filenames.append("tmp/more-" + name)
            filenames.append("tmp/" + name)
            images.append(discord.File("tmp/more-" + name))

        if not images:
            return await ctx.send("Please send valid image!")
        await ctx.send("Done!", files=images)

        try:
            for fil in filenames:
                os.remove(fil)
        except BaseException:
            pass

    @commands.command()
    async def choose(self, ctx, *, args):
        """Choose one of a lot arguments, splitted by a `|`."""
        choices = args.split("|")
        for i in range(len(choices)):
            if not choices[i].strip():
                return await ctx.send(f"Argument number {i+1} is invalid.")
        if len(choices) < 2:
            await ctx.send("You need to send at least 2 arguments!")
            return
        picked = random.choice(choices).strip()
        cleaned = discord.utils.escape_mentions(picked)
        await ctx.send(cleaned + ", of course!")

    @commands.command()
    async def roll(self, ctx, n: typing.Optional[int] = 10):
        """Roll a number from 1 to n."""
        res = random.randint(1, n)
        await ctx.send(f"{ctx.author.name} rolled {res} point(s).")

    @commands.command(name="8ball")
    async def eight_ball(self, ctx):
        """Rolls a magic 8-ball."""
        answers = [
            "Certainly.",
            "No doubt!",
            "Yes - definitely.",
            "Most likely.",
            "Yes.",
            "Probably.",
            "Maybe.",
            "Could be.",
            "Possibly.",
            "There's a chance.",
            "idk.",
            "Can't tell.",
            "Unsure.",
            "Ask again later.",
            "Dunno.",
            "No.",
            "Obviously not.",
            "I doubt it.",
            "Nope.",
            "Doesn't look good.",
        ]
        await ctx.send(random.choice(answers))


def setup(bot):
    bot.add_cog(Fun(bot))
