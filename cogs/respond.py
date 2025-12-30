from discord.ext import commands
import asyncio
import random
import os

constant_delay = 0.5
history_path = "responses/history.txt"

os.makedirs(os.path.dirname(history_path), exist_ok=True)

# If history.txt doesn't exist yet, write an empty file
if not os.path.exists(history_path):
    with open(history_path, "w") as f:
        pass

class Respond(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if self.bot.user.mentioned_in(message):
            response, delay = await self.choose_response(message.content.strip())
            await asyncio.sleep(constant_delay)
            async with message.channel.typing():
                await asyncio.sleep(delay) 
                await message.channel.send(response)
        else:
            await self.bot.process_commands(message)


    async def choose_response(self, message):
        if message[-1] == "?":
            return select_from_file("question.txt")
        else:
            return select_from_file("generic.txt")
                    
def select_from_file(filename):
        with open("responses/" + filename) as fp:
            lines = fp.read().splitlines()
            index = get_history_index(filename, len(lines))
            line = lines[index % len(lines)]
            split_line = line.split("\t")
            return split_line[0], float(split_line[1])

def get_history_index(filename, line_count):
    with open(history_path, "r+") as history_fp:
        lines = history_fp.read().splitlines()
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
        history_fp.seek(0)
        for i in range(len(lines)):
            lines[i] = "\t".join(lines[i])
        history_fp.write("\n".join(lines))
        history_fp.truncate()   # File can get smaller when it goes from double digit to single digit index
        return index

async def setup(bot):
    await bot.add_cog(Respond(bot))

if __name__ == "__main__":
    print(select_from_file("question.txt"))