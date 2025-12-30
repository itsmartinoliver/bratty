import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True

class QuestionBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.load_extension("cogs.questions")
        await self.load_extension("cogs.show_and_tell")
        await self.load_extension("cogs.respond")

bot = QuestionBot(intents)

@bot.command()
@commands.has_permissions(administrator=True)
async def reload(ctx, extension):
    try:
        await bot.reload_extension(f"cogs.{extension}")
        await ctx.send(f"Successfully reloaded `{extension}`")
    except Exception as e:
        await ctx.send(f"Failed to reload: `{e}`")

bot.run(TOKEN)
