from discord.ext import commands

import random
import requests
import json
import csv
import MessageFunctions as mf

class MiscCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Simulates rolling dice.')
    async def roll_dice(self, ctx):
        response = random.choice([1, 2, 3, 4, 5, 6])
        await ctx.send(response)


    @commands.command(help='Insults the target user.')
    async def insult(self, ctx, username: str):

        with open('RefFiles/english-nouns.txt', newline='') as f:
            reader = csv.reader(f)
            nouns = list(reader)
            f.close()

        with open('RefFiles/english-adjectives.txt', newline='') as f:
            reader = csv.reader(f)
            adjectives = list(reader)
            f.close()

        noun = random.choice(nouns)[0]
        adjective = random.choice(adjectives)[0]
        response = f"**{username}, you are a {adjective} {noun}.**"
        await ctx.send(response)


    @commands.command(help="Shows a inspirational quote.")
    async def inspirational_quote(self, ctx):
        response = f"**{get_quote()}**"
        await ctx.send(response)

    @commands.command(help="Converts input number to roman numerals.")
    async def roman_numeral(self, ctx, number: int):
        response = f"**{number} in Roman numerals is: {mf.to_rn(number)}**"
        await ctx.send(response)


def setup(bot):
    bot.add_cog(MiscCommands(bot))

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]["q"]
    author = json_data[0]["a"]
    return f"{quote} - {author}"