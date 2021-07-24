from discord.ext import commands

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



def setup(bot):
    bot.add_cog(MusicCommands(bot))