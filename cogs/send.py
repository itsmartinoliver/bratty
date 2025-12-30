from discord.ext import commands

class Send(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def send(self, ctx, channelID, message):
        channel = self.bot.get_channel(int(channelID))
        if channel:
            await channel.send(message)

async def setup(bot):
    await bot.add_cog(Send(bot))