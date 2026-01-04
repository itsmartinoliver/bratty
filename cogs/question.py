import datetime
import importlib
from zoneinfo import ZoneInfo
from discord.ext import commands, tasks
import question_data.question_selection as question_selection

importlib.reload(question_selection)    # Reloading the cog also reloads the question_selection module

class Question(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if "question" not in bot.config:
            bot.config["question"] = {
                "channel": "0",
                "role": "0",
                "hour": "8",
                "minute": "0"
            }

        self.channel = int(bot.config["question"]["channel"])
        self.role = int(bot.config["question"]["role"])
        self.hour = int(bot.config["question"]["hour"])
        self.minute = int(bot.config["question"]["minute"])
        self.timezone = ZoneInfo(bot.config["global"]["timezone"])

        self.daily_question.change_interval(time=datetime.time(hour=self.hour, minute=self.minute, tzinfo=self.timezone))
        self.daily_question.start()

        bot.save_config()


    def cog_unload(self):
        self.daily_question.cancel()
    
    @tasks.loop(time=datetime.time(hour=0)) # Loop timing is changed in the constructor
    async def daily_question(self):
        question_choice = question_selection.choose_question()
        await self.post_thread(question_choice)

    async def post_thread(self, content):
        channel = self.bot.get_channel(self.channel)
        if channel:
            date = datetime.datetime.now(self.timezone).strftime("%m/%d/%Y")
            message = await channel.send(f"## Question of the Day: {date}")
            thread = await message.create_thread(name=f"{content}", auto_archive_duration = 60*24)
            await thread.send(f"<@&{self.role}>: {content}")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def test_question(self, ctx):
        await self.daily_question()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear_history(self, ctx):
        question_selection.clear_history()

async def setup(bot):
    await bot.add_cog(Question(bot))