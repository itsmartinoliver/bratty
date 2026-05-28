import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import json
import traceback


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
                    "timezone": "America/Chicago",
                    "debug_channel": "0"
                }
            }
            self.save_config()

    async def setup_hook(self):
        await self.load_extension("cogs.question")
        # await self.load_extension("cogs.show_tell")
        await self.load_extension("cogs.respond")
        await self.load_extension("cogs.send")
        await self.load_extension("cogs.quip")

    async def on_ready(self):
        await self.debug("Setup Complete")

    async def debug(self, message):
        print(message, flush=True)
        try:
            debug_channel = bot.get_channel(int(bot.config["global"]["debug_channel"]))
            if debug_channel:
                await debug_channel.send(message)
        except:
            pass

    async def on_command_error(self, ctx, error):
        error_str = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        await self.debug("```\n" + error_str+"\n```")
        raise error
        
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
            bot.save_config()
            return True, None
        else:
            return False, f"{field} not found"
    except Exception as e:
        return False, str(e)

@bot.command()
@commands.has_permissions(administrator=True)
async def mod_config(ctx, cog, field, arg = None):
    try:
        if(field in bot.config[cog]):
            if not arg:
                bot.config[cog].pop(field)
                await ctx.send(f"Removed Config: `{cog}/{field}`")
            else:
                config(ctx, cog, field, arg, None)
        else:
            bot.config[cog][field] = arg
            await ctx.send(f"Added Config: `{cog}/{field} = {bot.config[cog][field]}`")
        bot.save_config()
    except Exception as e:
        pass

bot.run(TOKEN)

