import os
import discord
from discord.ext import commands
import asyncio
import json

intents = discord.Intents.all()
intents.voice_states = True

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

TOKEN = config["discord_token"]
bot = commands.Bot(command_prefix='!', intents=intents)

async def play_music(ctx, voice_channel, text_channel, music_folder, played_files):
    music_files = [f for f in os.listdir(music_folder) if f.endswith('.mp3')]

    for filename_with_extension in music_files:
        filename = os.path.splitext(filename_with_extension)[0]  
        file_path = os.path.join(music_folder, filename_with_extension)
            
        if os.path.exists(file_path) and filename not in played_files:
            voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            voice_client.stop()
            voice_client.play(discord.FFmpegPCMAudio(file_path))
            embed = discord.Embed(title="Song will play", description=filename, color=0x00ff00)
            await text_channel.send(embed=embed)
            while voice_client.is_playing():
                await asyncio.sleep(1)
                
            played_files.add(filename)
        else:
            print(f"File {filename_with_extension} Not found or already played!")
    
    played_files.clear()
    await setup(ctx, voice_channel.id, text_channel.id)  

@bot.command(name='setup')
@commands.has_permissions(administrator=True)
async def setup(ctx, voice_channel_id: int, text_channel_id: int):
    voice_channel = bot.get_channel(voice_channel_id)
    text_channel = bot.get_channel(text_channel_id)
    
    if not voice_channel:
        await ctx.send("no valid Voice Channel ID!")
        return
    
    if not text_channel:
        await ctx.send("no valid Text Channel ID!")
        return
    
    await voice_channel.connect()
    
    music_folder = "Music"
    played_files = set()

    while True:
        await play_music(ctx, voice_channel, text_channel, music_folder, played_files)

bot.run(TOKEN)
