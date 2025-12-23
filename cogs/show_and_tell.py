import datetime
from zoneinfo import ZoneInfo
from discord.ext import commands, tasks

timezone = ZoneInfo("America/Chicago")

show_tell_time = 12
show_tell_day = 5   # Numerical day of the week. 5 = Saturday
show_tell_role = 1452705790543794258
show_tell_channel = 1452882274730250391

class ShowAndTell(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.show_tell.start()

    def cog_unload(self):
        self.show_tell.cancel()

    @tasks.loop(time=datetime.time(hour=show_tell_time, tzinfo=timezone))
    async def show_tell(self, override_date = False):
        if datetime.datetime.now(timezone).weekday() == show_tell_day or override_date:
            channel = self.bot.get_channel(show_tell_channel)
            if channel:
                await channel.send(f"<@&{show_tell_role}> **Weekly Show and Tell!**\nShare and tell us about something cool you made, experienced, are proud of, etc from the past week!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def test_show_tell(self, ctx):
        await self.show_tell(True)

async def setup(bot):
    await bot.add_cog(ShowAndTell(bot))