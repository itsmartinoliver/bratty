import datetime
import importlib
from zoneinfo import ZoneInfo
from discord.ext import commands, tasks
import os
import random

history_path = "question_data/history.txt"
questions_path = "question_data/questions.tsv"
date_format = "%m/%d/%Y"

os.makedirs(os.path.dirname(history_path), exist_ok=True)

# If history.txt doesn't exist yet, write an empty file
if not os.path.exists(history_path):
    with open(history_path, "w") as f:
        pass


class Question(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if "question" not in bot.config:
            bot.config["question"] = {
                "channel": "0",
                "role": "0",
                "hour": "8",
                "minute": "0",
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
        question_choice = await self.choose_question()
        await self.post_thread(question_choice)

    async def post_thread(self, content):
        channel = self.bot.get_channel(self.channel)
        thread_content = content
        if len(content) > 100:
            thread_content = thread_content[:97] + "..."
        if channel:
            date = datetime.datetime.now(self.timezone).strftime(date_format)
            message = await channel.send(f"## Question of the Day: {date}")
            thread = await message.create_thread(name=f"{thread_content}", auto_archive_duration = 60*24)
            await thread.send(f"<@&{self.role}>: {content}")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def test_question(self, ctx):
        await self.daily_question()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear_history(self, ctx):
        with open(history_path, "r+") as history_f:
            history_f.truncate(0)

    async def make_question_list(self):
        """
        Returns parallel lists:
            questions: contains each question as a string
            weights: contains the weightings of each question as a float
        """
        valid_questions = []
        time_now = datetime.datetime.now(self.timezone)
        hist_dict = self.make_hist_dict()

        with open(questions_path, "r") as questions_f:
            for line in questions_f.readlines()[1:]:  # skip header
                split_line = line.strip().split("\t")
                question = split_line[0]
                min_days = int(split_line[1]) if len(split_line) > 1 else -1
                # min_days == -1 indicates no repeats are allowed
                if self.is_valid(question, min_days, hist_dict, time_now):
                    valid_questions.append(question)
        await self.bot.debug(str(len(valid_questions)) + " valid questions remaining")
        return valid_questions

    def make_hist_dict(self):
        hist_dict = {}
        with open(history_path, "r") as history_f:
            for line in history_f.readlines():
                if line == "\n":
                    break
                split_line = line.strip().split("\t")
                hist_dict[split_line[0]] = datetime.datetime.strptime(split_line[1], date_format).replace(tzinfo=self.timezone)
        return hist_dict

    def is_valid(self, question, min_days, hist_dict, time_now):
        if question not in hist_dict:
            return True
        if min_days == -1:
            return False
        time_asked = hist_dict[question]
        time_since = time_now - time_asked
        return time_since >= datetime.timedelta(days=float(min_days))

    async def choose_question(self):
        questions = await self.make_question_list()
        question_choice = random.choice(questions)
        self.add_to_history(question_choice)
        return question_choice

    def add_to_history(self, new_entry):
        with open(history_path, "a") as history_f:
            history_f.write(new_entry + "\t" + datetime.datetime.now(self.timezone).strftime(date_format) + "\n")

async def setup(bot):
    await bot.add_cog(Question(bot))