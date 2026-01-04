import datetime
from discord.ext import commands, tasks
from zoneinfo import ZoneInfo
import os
import random

history_path = "quips/history.txt"

os.makedirs(os.path.dirname(history_path), exist_ok=True)

# If history.txt doesn't exist yet, write an empty file
if not os.path.exists(history_path):
    with open(history_path, "w") as f:
        pass


class Quip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if "quip" not in bot.config:
            bot.config["quip"] = {
                "daily_probability": "0.5",
                "start_hour": "9",
                "end_hour": "17",
                "start_minute": "0",
                "end_minute": "59",
                "channels": []
            }

        self.debug = bool(bot.config["quip"]["debug"])
        self.daily_probability = float(bot.config["quip"]["daily_probability"])
        self.start_time = int(bot.config["quip"]["start_time"])
        self.end_time = int(bot.config["quip"]["end_time"])
        self.channels = bot.config["quip"]["channels"]

        bot.save_config()

        @tasks.loop(time=datetime.time(hour=0)) # Loop timing is changed in the constructor
        async def plan_quip(self):
            rng = random.random()
            if random <= self.daily_probability:
                
            else:
                print("Quip not planned")
            await self.post_thread(question_choice)

async def setup(bot):
    await bot.add_cog(Quip(bot))
    