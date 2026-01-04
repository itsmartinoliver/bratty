import datetime
from discord.ext import commands, tasks
from zoneinfo import ZoneInfo
import os
import random

history_path = "quip_data/history.txt"
quip_path = "quip_data/quips.txt"

os.makedirs(os.path.dirname(history_path), exist_ok=True)

# If history.txt doesn't exist yet, write an empty file
if not os.path.exists(history_path):
    with open(history_path, "w") as f:
        pass

def clear_history():
    with open(history_path, "r+") as history_f:
        history_f.truncate(0)

class Quip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if "quip" not in bot.config:
            bot.config["quip"] = {
                "daily_probability": "0.5",
                "start_hour": "9",
                "end_hour": "16",
                "start_minute": "0",
                "end_minute": "59",
                "max_entries": "50",
                "channels": []
            }

        self.daily_probability = float(bot.config["quip"]["daily_probability"])
        self.start_hour = int(bot.config["quip"]["start_hour"])
        self.end_hour = int(bot.config["quip"]["end_hour"])
        self.start_minute = int(bot.config["quip"]["start_minute"])
        self.end_minute = int(bot.config["quip"]["end_minute"])
        self.max_entries = int(bot.config["quip"]["max_entries"])
        self.channels = bot.config["quip"]["channels"]
        self.timezone = ZoneInfo(bot.config["global"]["timezone"])

        self.plan_quip.change_interval(time=datetime.time(hour=0, tzinfo=self.timezone))
        self.plan_quip.start()

        bot.save_config()

    def cog_unload(self):
        self.plan_quip.cancel()
        if self.send_quip.is_running:
            self.send_quip.cancel()

    @tasks.loop(time=datetime.time(hour=0)) # Loop timing timezone is set by constructor
    async def plan_quip(self):
        rng = random.random()
        if rng <= self.daily_probability:
            quip_hour = random.randint(self.start_hour, self.end_hour)
            quip_minute = random.randint(self.start_minute, self.end_minute)

            if self.send_quip.is_running:
                self.send_quip.stop()
            self.send_quip.change_interval(time=datetime.time(hour=quip_hour, minute=quip_minute, tzinfo=self.timezone))
            self.send_quip.start()
            print(f"Quip planned for {quip_hour}:{quip_minute:02d}", flush=True)
        else:
            self.send_quip.stop()
            print("Quip not planned", flush=True)


    @tasks.loop(time=datetime.time(hour=0)) # Loop timing will be changed by plan_quip
    async def send_quip(self):
        channelID = int(random.choice(self.channels))
        channel = self.bot.get_channel(channelID)
        quip = self.choose_quip()
        await channel.send(quip)
        
    def choose_quip(self):
        with open(quip_path, "r") as quip_fp:
            quips = quip_fp.read().splitlines()
        with open(history_path, "r") as history_fp:
            history = history_fp.read().splitlines()

        quip_choice = random.choice(quips)
        while quip_choice in history:
            quip_choice = random.choice(quips)

        self.add_to_history(quip_choice)
        return quip_choice
        
    def add_to_history(self, new_entry):
        with open(history_path, "r") as history_f:
            lines = history_f.read().splitlines()
            while len(lines) >= self.max_entries:
                lines.pop(0)    # remove the top line, which is the oldest entry
            lines.append(new_entry)    # final entry did not previously have a new line, must add it now
        
        with open(history_path, "w") as history_f:
            history_f.write("\n".join(lines))


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def test_plan_quip(self, ctx):
        await self.plan_quip()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def test_send_quip(self, ctx):
        await self.send_quip()

async def setup(bot):
    await bot.add_cog(Quip(bot))
    