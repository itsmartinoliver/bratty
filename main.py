import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import json

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
config_path = "config.json"

class BrattyBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix="!", intents=intents)

        if os.path.exists(config_path):
            with open(config_path) as f:
                self.config = json.load(f)
        else:
            self.config = {
                "global": {
                    "timezone": "America/Chicago"
                }
            }
            self.save_config()

    async def setup_hook(self):
        await self.load_extension("cogs.question")
        await self.load_extension("cogs.show_tell")
        await self.load_extension("cogs.respond")
        await self.load_extension("cogs.send")
        await self.load_extension("cogs.quip")


    def save_config(self):
        with open(config_path, "w") as f:
            json.dump(self.config, f, indent=4)
            
bot = BrattyBot(intents)

@bot.command()
@commands.has_permissions(administrator=True)
async def reload(ctx, extension):
    try:
        await bot.reload_extension(f"cogs.{extension}")
        await ctx.send(f"Successfully reloaded `{extension}`")
    except Exception as e:
        await ctx.send(f"Failed to reload: `{e}`")

@bot.command()
@commands.has_permissions(administrator=True)
async def config(ctx, cog = None, field = None, arg1 = None, arg2 = None):
    if(cog == None):
        await ctx.send("```\n"+json.dumps(bot.config, indent=4)+"\n```")
        return
    success, fail_message = update_config(cog, field, arg1, arg2)
    if success:
        await ctx.send(f"Updated Config: `{cog}/{field} = {bot.config[cog][field]}`")
    else:
        await ctx.send(f"Failed to Update Config: `{fail_message}`")

def update_config(cog, field, arg1, arg2):
    try:
        if(field in bot.config[cog]):
            if(type(bot.config[cog][field]) == list):
                match arg1:
                    case "clear":
                        bot.config[cog][field] = []
                    case "add":
                        bot.config[cog][field].append(arg2)
                        bot.config[cog][field] = list(set(bot.config[cog][field]))
                    case "remove":
                        bot.config[cog][field].remove(arg2)
                    case _:
                        return False, f"invalid list operation '{field}'"
            else:
                bot.config[cog][field] = arg1
            return True, None
        else:
            return False, f"{field} not found"
    except Exception as e:
        return False, str(e)

bot.run(TOKEN)
