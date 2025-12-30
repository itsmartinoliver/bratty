import datetime
from zoneinfo import ZoneInfo
from discord.ext import commands, tasks

class ShowAndTell(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if "show_tell" not in bot.config:
            bot.config["show_tell"] = {
                "weekday": "5",
                "hour": "12",
                "minute": "0",
                "role": "0",
                "channel": "0"
            }

        self.weekday = int(bot.config["show_tell"]["weekday"])
        self.hour = int(bot.config["show_tell"]["hour"])
        self.minute = int(bot.config["show_tell"]["minute"])
        self.role = int(bot.config["show_tell"]["role"])
        self.channel = int(bot.config["show_tell"]["channel"])
        self.timezone = ZoneInfo(bot.config["global"]["timezone"])

        self.show_tell.change_interval(time=datetime.time(hour=self.hour, minute=self.minute, tzinfo=self.timezone))
        self.show_tell.start()

        bot.save_config()

    def cog_unload(self):
        self.show_tell.cancel()

    @tasks.loop(time=datetime.time(hour=0)) # Loop timing is changed in the constructor
    async def show_tell(self, override_date = False):
        if datetime.datetime.now(self.timezone).weekday() == self.weekday or override_date:
            channel = self.bot.get_channel(self.channel)
            if channel:
                await channel.send(f"<@&{self.role}> **Weekly Show and Tell!**\nShare and tell us about something cool you made, experienced, are proud of, etc from the past week!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def test_show_tell(self, ctx):
        await self.show_tell(True)

async def setup(bot):
    await bot.add_cog(ShowAndTell(bot))