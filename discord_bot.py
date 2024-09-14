from credentials import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID
import discord
from discord import *
from time import sleep
from discord.ext import commands, tasks

BOT_TOKEN = DISCORD_BOT_TOKEN
CHANNEL_ID = DISCORD_CHANNEL_ID

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True 

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}.")
    job_loop.start()
    
async def hello():
    channel = await client.fetch_channel(CHANNEL_ID)
    await channel.send("Hello, World!")


@tasks.loop(seconds=5)
async def job_loop():
    await hello()
    print("sleeping for 5 seconds")

client.run(BOT_TOKEN)




