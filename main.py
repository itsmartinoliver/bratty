import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import json

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True

class BrattyBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix="!", intents=intents)

        self.config_path = "config.json"
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                self.config = json.load(f)
        else:
            self.config = {
                "global": {
                    "timezone": "America/Chicago"
                }
            }
            self.save_config()

    async def setup_hook(self):
        await self.load_extension("cogs.questions")
        await self.load_extension("cogs.show_tell")
        await self.load_extension("cogs.respond")
        await self.load_extension("cogs.send")


    def save_config(self):
        with open(self.config_path, "w") as f:
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
async def config(ctx, cog = None, field = None, value = None):
    if(cog == None):
        await ctx.send("```\n"+json.dumps(bot.config, indent=4)+"\n```")
        return
    try:
        if(field in bot.config[cog]):
            bot.config[cog][field] = value
            await ctx.send(f"Updated config: `{cog}/{field} = {value}`")
            bot.save_config()
        else:
            await ctx.send(f"Failed to update config: `{field} not found`")
    except Exception as e:
        await ctx.send(f"Failed to update config: `{e}`")

bot.run(TOKEN)
