import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import datetime
from zoneinfo import ZoneInfo

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True

timezone = ZoneInfo("America/Chicago")

# Time is hours in 24H format when the question gets sent
question_time = 8
question_role = 1452705714832408616
question_channel = 1452075722784116878

show_tell_time = 12
show_tell_day = 5   # Numerical day of the week. 5 = Saturday
show_tell_role = 1452705790543794258
show_tell_channel = 1452882274730250391

archive_duration = 60 * 24

class QuestionBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
    
    # Implicitly called by the discord package
    async def setup_hook(self):
        self.daily_question.start()
        self.show_tell.start()

    @tasks.loop(time=datetime.time(hour=question_time, minute=2, tzinfo=timezone))
    async def daily_question(self):
        await self.post_thread("abc")

    @tasks.loop(time=datetime.time(hour=show_tell_time, tzinfo=timezone))
    async def show_tell(self):
        if datetime.datetime.now(timezone).weekday() == show_tell_day:
            channel = self.get_channel(show_tell_channel)
            if channel:
                await channel.send(f"<@&{show_tell_role}> **Weekly Show and Tell!**\nShare and tell us about something cool you made, experienced, are proud of, etc from the past week!")

    async def post_thread(self, content):
        channel = self.get_channel(question_channel)
        if channel:
            date = datetime.datetime.now(timezone).strftime("%m/%d/%Y")
            message = await channel.send(f"## Question of the Day: {date}")
            thread = await message.create_thread(name=f"{content}", auto_archive_duration = archive_duration)
            await thread.send(f"<@&{question_role}>: {content}")


bot = QuestionBot()

@bot.command()
@commands.has_permissions(manage_messages=True)
async def test_question(ctx):
    await bot.post_thread("question content", question_role)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def test_show(ctx):
    await bot.show_tell()

bot.run(TOKEN)
