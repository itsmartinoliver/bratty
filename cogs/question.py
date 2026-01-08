import datetime
import importlib
from zoneinfo import ZoneInfo
from discord.ext import commands, tasks
import os
import random

history_path = "question_data/history.txt"
questions_path = "question_data/questions.tsv"

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
                "max_entries": "50"
            }

        self.channel = int(bot.config["question"]["channel"])
        self.role = int(bot.config["question"]["role"])
        self.hour = int(bot.config["question"]["hour"])
        self.minute = int(bot.config["question"]["minute"])
        self.max_entries = int(bot.config["question"]["max_entries"])
        self.timezone = ZoneInfo(bot.config["global"]["timezone"])

        self.daily_question.change_interval(time=datetime.time(hour=self.hour, minute=self.minute, tzinfo=self.timezone))
        self.daily_question.start()

        bot.save_config()


    def cog_unload(self):
        self.daily_question.cancel()
    
    @tasks.loop(time=datetime.time(hour=0)) # Loop timing is changed in the constructor
    async def daily_question(self):
        question_choice = self.choose_question()
        await self.post_thread(question_choice)

    async def post_thread(self, content):
        channel = self.bot.get_channel(self.channel)
        thread_content = content
        if len(content) > 100:
            thread_content = thread_content[:97] + "..."
        print(len(thread_content))
        if channel:
            date = datetime.datetime.now(self.timezone).strftime("%m/%d/%Y")
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

    def make_question_lists(self):
        """
        Returns parallel lists:
            questions: contains each question as a string
            weights: contains the weightings of each question as a float
        """
        questions = []
        weights = []
        with open(questions_path, "r") as questions_f:
            for line in questions_f.readlines()[1:]:  # skip header
                split_line = line.split("\t")
                questions.append(split_line[0].strip()) # strip() is just for safety, shouldn't normally have any effect
                weights.append(float(split_line[1]))
        return questions, weights

    def remove_recent(self, questions, weights):
        """
        Produces new parallel lists (questions, weights) containing only the questions that
        do NOT appear in history.txt
        """
        if(len(questions) != len(weights)):
            raise RuntimeError("Questions and Weights do not have the same length")

        history_entries = []
        with open(history_path, "r") as history:
            for line in history.readlines():
                history_entries.append(line.strip())
        new_questions = []
        new_weights = []

        for i in range(len(questions)):
            if questions[i] not in history_entries:
                new_questions.append(questions[i])
                new_weights.append(weights[i])

        return new_questions, new_weights

    def choose_question(self):
        questions, weights = self.make_question_lists()
        questions, weights = self.remove_recent(questions, weights)
        # Using random.choices to utilize weights. This returns a list, so we need to index the element
        question_choice = random.choices(questions, weights=weights)[0]
        self.add_to_history(question_choice)
        return question_choice

    def add_to_history(self, new_entry):
        with open(history_path, "r") as history_f:
            lines = history_f.read().splitlines()
            while len(lines) >= self.max_entries:
                lines.pop(0)    # remove the top line, which is the oldest entry
            lines.append(new_entry)    # final entry did not previously have a new line, must add it now
        
        with open(history_path, "w") as history_f:
            history_f.write("\n".join(lines))

async def setup(bot):
    await bot.add_cog(Question(bot))