from discord.ext import commands
import asyncio
import os
import time

history_path = "responses/history.txt"
user_pings = {}
total_pings = []

os.makedirs(os.path.dirname(history_path), exist_ok=True)

# If history.txt doesn't exist yet, write an empty file
if not os.path.exists(history_path):
    with open(history_path, "w") as f:
        pass

class Respond(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if "respond" not in bot.config:
            bot.config["respond"] = {
                "constant_delay": "0.5",
                "user_ping_threshold": "5",
                "total_ping_threshold": "10",
                "time_threshold": "3600",
                "crashout_channel": "0",
                "owner_userID": "0"
            }

        self.constant_delay = float(bot.config["respond"]["constant_delay"])
        self.user_ping_threshold = int(bot.config["respond"]["user_ping_threshold"])
        self.total_ping_threshold = int(bot.config["respond"]["total_ping_threshold"])
        self.time_threshold = int(bot.config["respond"]["time_threshold"])
        self.crashout_channel = int(bot.config["respond"]["crashout_channel"])
        self.owner_userID = int(bot.config["respond"]["owner_userID"])


        bot.save_config()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if self.bot.user.mentioned_in(message):
            response, delay = await self.choose_response(message)
            response = response.replace("{SENDER}", f"{message.author.mention}")
            response = response.replace("{OWNER}", f"<@{self.owner_userID}>")

            if response == "":
                return  # Bratty chooses to ignore
            await asyncio.sleep(self.constant_delay)
            async with message.channel.typing():
                await asyncio.sleep(delay) 
                await message.channel.send(response)


    async def choose_response(self, message):
        user_ping_count, total_ping_count = count_recent_pings(message, self.time_threshold)
        if total_ping_count > self.total_ping_threshold:
            return "", 0    # Send nothing
        
        if total_ping_count == self.total_ping_threshold - 1:
            asyncio.create_task(self.crashout())
            # Trigger the crashout message but don't return, as it should select the proper category for the main response

        if user_ping_count == self.user_ping_threshold:
            return select_from_file("berate.txt")
        if total_ping_count == self.total_ping_threshold:
            return select_from_file("logoff.txt")
        if "clanker" in message.content.lower():
            return select_from_file("clank.txt")
        if len(message.mentions) > 1:
            return select_from_file("tagged.txt")
        if message.content.strip()[-1] == "?":
            return select_from_file("question.txt")
        else:
            return select_from_file("generic.txt")
                    
    async def crashout(self):
        response, delay = select_from_file("crashout.txt")
        channel = self.bot.get_channel(self.crashout_channel)
        if channel:
            async with channel.typing():
                await asyncio.sleep(delay) 
                await channel.send(response)

            
def select_from_file(filename):
        with open("responses/" + filename) as f:
            lines = f.read().splitlines()
            index = get_history_index(filename, len(lines))
            line = lines[index % len(lines)]
            split_line = line.split("\t")
            return split_line[0], float(split_line[1])

def get_history_index(filename, line_count):
    with open(history_path, "r+") as history_f:
        lines = history_f.read().splitlines()
        in_history = False
        for i in range(len(lines)):
            lines[i] = lines[i].split("\t")
            if(lines[i][0] == filename):
                index = int(lines[i][1])
                in_history = True
                lines[i][1] = str((int(lines[i][1]) + 1) % line_count)
        if not in_history:
            index = 0
            lines.append([filename, "1"])
            # Going to use the first one (0) right away, so start the counter at 1
        history_f.seek(0)
        for i in range(len(lines)):
            lines[i] = "\t".join(lines[i])
        history_f.write("\n".join(lines))
        history_f.truncate()   # File can get smaller when it goes from double digit to single digit index
        return index
    
def count_recent_pings(message, time_threshold):
    user_id = message.author.id
    timestamp = time.time()
    if user_id not in user_pings:
        user_pings[user_id] = []
    user_pings[user_id].append(timestamp)
    total_pings.append(timestamp)
    
    user_pings[user_id] = [ping_time for ping_time in user_pings[user_id] if timestamp - ping_time < time_threshold]
    
    i = 0
    while i < len(total_pings):
        if timestamp - total_pings[i] >= time_threshold:
            total_pings.pop(i)
        else:
            i += 1

    return len(user_pings[user_id]), len(total_pings)

async def setup(bot):
    await bot.add_cog(Respond(bot))

if __name__ == "__main__":
    print(select_from_file("question.txt"))