
import discord
from discord.ext import commands
from discord import abc as d_abc
import youtube_dl
from youtube_dl import YoutubeDL
import os
import random
import csv
import requests
import json
import urllib.request
import re
import asyncio
from googletrans import Translator, client

import MessageFunctions as mf

# Music functionally requires PyNaCl and FFMPEG

# ------------------------------------------------------------------------------------------ GLOBALS

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
MUSIC_QUEUE = []
# ------------------------------------------------------------------------------------------


def get_yt_url(keywords : str):
    keywords = keywords.replace(' ', '%')
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + keywords)
    videos_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    return "https://www.youtube.com/watch?v=" + videos_ids[0]

def ytdl_search(arg):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            requests.get(arg) 
        except:
            video = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        else:
            video = ydl.extract_info(arg, download=False)

    return video
# ------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------


bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}, {bot.user.id}')

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("**ERROR: Invalid command used.**")

@bot.event
async def on_message(message):
    await bot.process_commands(message)




@bot.command(help="Search Youtube for videos with prompt.", )
async def yt_search(ctx):
    search_terms = ctx.message.content.replace("!yt_search ", "")
    response = f"**YouTube result for \"{search_terms}\"**\n" + ytdl_search(search_terms)["webpage_url"]
    await ctx.send(response)


@bot.command(help="Encodes the input into morse code. (Only available via "
                                                          "direct message)")
async def encode_morse(ctx):
    if not isinstance(ctx.message.channel, d_abc.GuildChannel):
        in_message = ctx.message.content.replace("!encode_morse ", "")
        response = mf.encode_morse(in_message)
        await ctx.send("**" + response + "**")
    else:
        response = "This command is only available via direct messages."
        await ctx.send("**" + response + "**")


@bot.command(help="Decodes the input morse code into text.")
async def decode_morse(ctx):
    in_message = ctx.message.content.replace("!decode_morse ", "")
    response = mf.decode_morse(in_message)
    await ctx.send("**" + response + "**")


@bot.command(help="Encrypts the input text using SHA256 - password must be in "
                                                         "square brackets. (NOT FOR SENSITIVE INFORMATION)")
async def aes_encrypt(ctx):
    if not isinstance(ctx.message.channel, d_abc.GuildChannel):
        if ctx.message.content.count("[") == 1 and ctx.message.content.count("]") == 1:
            raw_input = ctx.message.content.replace("!aes_encrypt ", "")
            password = raw_input[raw_input.find("[") + 1:raw_input.find("]")]
            message = raw_input.replace("[" + password + "]", "")
            response = mf.aes_encrypt(message, password)
            await ctx.send("**" + response + "**")
        else:
            response = "Invalid command structure. Message must have only one \"[\" and \"]\"."
            await ctx.send("**" + response + "**")
    else:
        response = "This command is only available via direct messages."
        await ctx.send("**" + response + "**")


@bot.command(help="Decrypts the input text using SHA256 - password must be in "
                                                         "square brackets. (NOT FOR SENSITIVE INFORMATION)")
async def aes_decrypt(ctx):
    if ctx.message.content.count("[") == 1 and ctx.message.content.count("]") == 1:
        raw_input = ctx.message.content.replace("!aes_decrypt ", "")
        password = raw_input[raw_input.find("[") + 1:raw_input.find("]")]
        message = raw_input.replace("[" + password + "]", "")
        decrypted = mf.aes_decrypt(message, password)
        if decrypted is not None:
            await ctx.send("**" + decrypted + "**")
        else:
            response = "Invalid password."
            await ctx.send("**" + response + "**")
    else:
        response = "Invalid command structure. Message must have only one \"[\" and \"]\"."
        await ctx.send("**" + response + "**")


@bot.command(help="Translate the message into the target language. Target language must be in square brackets in ISO-639-1 code.")
async def translate(ctx):
    if ctx.message.content.count("[") == 1 and ctx.message.content.count("]") == 1:
        raw_input = ctx.message.content.replace("!translate ", "")
        target_language = raw_input[raw_input.find("[") + 1:raw_input.find("]")]
        message = raw_input.replace("[" + target_language + "]", "")

        translation = mf.translate(message,target_language)
        if translation != None:
            await ctx.send("**Translated message: " + translation + "**")
        else:
            await ctx.send("**Error translating message. Either the message is already in the target language or the ISO code is invalid. ISO codes are available at: https://cloud.google.com/translate/docs/languages**")
    else:
        await ctx.send("**Invalid command structure. Message must have only one \"[\" and \"]\".**")


@bot.command(help="Plays music from YouTube matching the input query.")
async def music_play(ctx):

    voice_channel = ctx.author.voice.channel
    await voice_channel.connect()
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    
    raw_input = ctx.message.content.replace("!music_play ", "")
    video = ytdl_search(raw_input)
    MUSIC_QUEUE.append([video["webpage_url"], video["title"]])
    
    await play_audio(voice, ctx)

def download_audio(url):
    ydl_opts = {
        "format" : "249/250/251",
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        # If there's already a song downloaded then delete it
        music_audio_there = os.path.isfile("music_audio.webm")
        if music_audio_there:
            os.remove("music_audio.webm")
        
        # Download the new audio
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".webm"):
            os.rename(file, "music_audio.webm")

async def play_audio(voice, ctx):
    global MUSIC_QUEUE
    try:
        if MUSIC_QUEUE:
            url = MUSIC_QUEUE[0][0]
            title = MUSIC_QUEUE[0][1]
            download_audio(url)
            MUSIC_QUEUE.pop(0)
        await ctx.send("Now playing: " + title)
        await voice.play(discord.FFmpegOpusAudio("music_audio.webm"),after = lambda e: asyncio.run_coroutine_threadsafe(play_audio(voice, ctx), bot.loop))
    except TypeError:
        pass


@bot.command()
async def music_queue(ctx):
    global MUSIC_QUEUE
    raw_input = ctx.message.content.replace("!music_queue ", "")
    video = ytdl_search(raw_input)
    MUSIC_QUEUE.append([video["webpage_url"], video["title"]])
    await ctx.send(video["title"] + " has been queued")

@bot.command()
async def music_leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        ctx.send("**Bot is not connected to any voice channel that it can leave.**")

@bot.command()
async def music_pause(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        ctx.send("**No audio is currently playing.**")

@bot.command()
async def music_resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        ctx.send("**Cannot resume playing as the audio is not paused.**")

@bot.command()
async def music_stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()

@bot.command(help="Shuts down the bot. Owner only command.")
@commands.is_owner()
async def shutdown(context):
    exit()

@bot.command(help="Searches Wikipedia for a page summary of the input query.")
async def wiki(ctx):
    raw_input = ctx.message.content.replace("!wiki ", "")
    response = mf.get_wiki_summary(raw_input)
    await ctx.send(f"**Wikipedia results for {raw_input}**:\n{response}")


extensions = ["cogs.MiscCommands"]

for extension in extensions:
    bot.load_extension(extension)

TOKEN = ""
bot.run(TOKEN)
