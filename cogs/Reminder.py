import re
from datetime import datetime, timedelta

import discord
from bson.errors import InvalidId
from bson.objectid import ObjectId
from discord.ext import commands

from db.Reminder import Reminder as ReminderDB

eta_re = re.compile(
    r"(?:(?P<days>\d+)d)?(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?(?:(?P<seconds>\d+)s)?"
)

MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR


def format_time(s):
    days = int(s // DAY)
    s %= DAY
    hours = int(s // HOUR)
    s %= HOUR
    minutes = int(s // 60)
    s %= MINUTE
    seconds = int(s % 60)

    return f"{days}d{hours}h{minutes}m{seconds}s"


class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tasks = {}

    @commands.Cog.listener()
    async def on_ready(self):
        await self.init()

    def _get_existing(self, uid=None):
        kwargs = {}
        if uid:
            kwargs = {"user_id": uid}
        return ReminderDB.find(kwargs)

    async def _cleanup(self, reminder):
        self.tasks.pop(str(reminder.id))
        await reminder.delete()

    def send_reminder(self, reminder, error=None):
        if error:
            raise error
        if not reminder:
            return
        delay = reminder.datetime.timestamp() - datetime.utcnow().timestamp()
        late = False
        if delay < -10:
            # We restarted and now we're late to things lol
            late_by = abs(delay)
            delay = 1
            late = True

        async def send():
            # TODO: Somehow make em tidier
            # Fetch the user, then the channel. If both of them doesn't exist,
            # just cancel them, as there is no need to proceed since we can't send anyway.
            try:
                user = await self.bot.fetch_user(reminder.user_id)
            except discord.HTTPException:
                user = None

            try:
                channel = await self.bot.fetch_channel(reminder.channel_id)
            except discord.HTTPException:
                if user:
                    target = user
                else:
                    # Don't know what to do, just cancel it.
                    return await self._cleanup(reminder)
            else:
                target = channel
                try:
                    await channel.fetch_message(reminder.message_id)
                except discord.NotFound:
                    return await self._cleanup(reminder)

            reminder_str = f"{user.mention}\r:alarm_clock: Reminder! {reminder.content}"
            if late:
                reminder_str += (
                    f"\rSorry, I am late by {format_time(round(late_by, 2))} :("
                )

            try:
                await target.send(reminder_str)
            except discord.DiscordException:
                pass
            finally:
                await self._cleanup(reminder)

        def callback():
            self.bot.loop.create_task(send())

        self.tasks[str(reminder.id)] = self.bot.loop.call_later(delay, callback)

    async def init(self):
        self._get_existing().each(callback=self.send_reminder)

    @commands.command()
    async def remind(self, ctx, eta, *, message):
        "Remind you things after a certain time."
        eta = eta_re.match(eta)
        days = int(eta["days"]) if eta["days"] else 0
        hours = int(eta["hours"]) if eta["hours"] else 0
        minutes = int(eta["minutes"]) if eta["minutes"] else 0
        seconds = int(eta["seconds"]) if eta["seconds"] else 0
        delta = timedelta(days=days, seconds=seconds, minutes=minutes, hours=hours)
        end_date = datetime.utcnow() + delta
        remind_data = ReminderDB(
            user_id=ctx.author.id,
            message_id=ctx.message.id,
            channel_id=ctx.channel.id,
            content=message,
            datetime=end_date,
        )
        await remind_data.commit()
        self.send_reminder(remind_data)
        await ctx.send(f"Reminder set! I will remind you on {end_date.isoformat(' ')}!")

    @commands.command()
    async def remind_list(self, ctx):
        "List of your running reminds."
        desc = "```ID                       | When (UTC)                 | Content\r"
        cursor = await self._get_existing(ctx.author.id).to_list(None)
        for reminder in cursor:
            desc += f"{reminder.id} | {reminder.datetime.isoformat(' ')} | {reminder.content}\r"
        desc += f"```\r{len(cursor)} reminders found."
        embed = discord.Embed(
            title="Reminder list", colour=discord.Colour(0x146BAA), description=desc
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def remind_delete(self, ctx, _id):
        "Cancel/delete running remind."
        try:
            _id = ObjectId(_id)
        except InvalidId:
            return await ctx.send("Invalid ID.")
        document = await ReminderDB.find_one({"_id": _id})
        if not document:
            return await ctx.send("Not found!")
        if document.user_id != ctx.author.id:
            return await ctx.send(
                "You are trying to delete a reminder that is not yours."
            )
        await document.delete()
        self.tasks[str(document.id)].cancel()
        await ctx.send("Done!")


def setup(bot):
    bot.add_cog(Reminder(bot))
