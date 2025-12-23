import datetime
import importlib
from zoneinfo import ZoneInfo
from discord.ext import commands, tasks
import question_data.question_selection as question_selection

importlib.reload(question_selection)    # Reloading the cog also reloads the question_selection module

timezone = ZoneInfo("America/Chicago")

# Time is hours in 24H format when the question gets sent
question_time = 8
question_role = 1452705714832408616
question_channel = 1452075722784116878

archive_duration = 60 * 24

class Questions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_question.start()

    def cog_unload(self):
        self.daily_question.cancel()
    
    @tasks.loop(time=datetime.time(hour=question_time, tzinfo=timezone))
    async def daily_question(self):
        question_choice = question_selection.choose_question()
        await self.post_thread(question_choice)

    async def post_thread(self, content):
        channel = self.bot.get_channel(question_channel)
        if channel:
            date = datetime.datetime.now(timezone).strftime("%m/%d/%Y")
            message = await channel.send(f"## Question of the Day: {date}")
            thread = await message.create_thread(name=f"{content}", auto_archive_duration = archive_duration)
            # await thread.send(f"<@&{question_role}>: {content}")
            await thread.send(f"{content}") # no ping for less annoying testing


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def test_question(self, ctx):
        await self.daily_question()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear_history(self, ctx):
        question_selection.clear_history()

async def setup(bot):
    await bot.add_cog(Questions(bot))