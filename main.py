import requests
from credentials import coc_api_key, clan_tag
from datetime import datetime, timezone
from war_information import War_information, demo_PREP_war, demo_FIGHT_war, demo_OVER_war
from credentials import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID
import discord
from discord import *
from time import sleep
from discord.ext import commands, tasks
import pytz
from credentials import coc_name_to_discord_id

headers = {"Authorization": f"Bearer {coc_api_key}"}

currentwar = f"https://api.clashofclans.com/v1/clans/{clan_tag}/currentwar"

warlog = f"https://api.clashofclans.com/v1/clans/{clan_tag}/warlog?limit=1"

current_war_information = None

def fetch_current_war() -> War_information:
    data = requests.get(currentwar, headers=headers).json()

    if data.get("state") == "notInWar":
        return None

    new_opponent = data.get("opponent").get("name")
    
    new_start_time_raw = data.get("startTime")
    new_start_time_raw = datetime.strptime(new_start_time_raw, "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=timezone.utc)

    # Convert to Germany timezone
    germany_timezone = pytz.timezone('Europe/Berlin') 
    new_start_time_local = new_start_time_raw.astimezone(germany_timezone)
    new_start_time = new_start_time_local.strftime("%d. %B %Y %H:%M:%S")

    # ... (Similarly for new_end_time)

    new_end_time_raw = data.get("endTime")
    new_end_time_raw = datetime.strptime(new_end_time_raw, "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=timezone.utc)

    # Convert to Germany timezone
    new_end_time_local = new_end_time_raw.astimezone(germany_timezone)
    new_end_time = new_end_time_local.strftime("%d. %B %Y %H:%M:%S")

    participants = []
    for member in data.get("clan").get("members"):
        participants.append(member.get("name"))
    
    return War_information(new_opponent, new_start_time, int(new_start_time_raw.timestamp()), new_end_time, int(new_end_time_raw.timestamp()), participants)

def fetch_results():
    return requests.get(warlog, headers=headers).json()

def print_war_information(war_information: War_information):
    # PREP DAY
    if war_information.is_upcoming():
        if not war_information.posted_prep_start:
            print("PREP DAY HAS STARTED!")
            war_information.posted_prep_start = True

    # WAR DAY
    if war_information.has_started() and not war_information.has_ended():
        if not war_information.posted_fight_start:
            print("FIGHT DAY HAS STARTED!")
            war_information.posted_fight_start = True

    # WAR OVER
    if war_information.has_ended():
        if not war_information.posted_results:
            print("WAR HAS ENDED!")
            war_information.posted_results = True



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

async def post_war_results():
    results = fetch_results()["items"][0]
    message = ""
    message += f":shield::crossed_swords::shield::crossed_swords::shield:\n"
    message += f"War against {results["opponent"]["name"]} ({results["opponent"]["tag"]}) has ended!\n"
    if results["result"] == "win":
        message += "We won!\n"
    elif results["result"] == "lose":
        message += "Unfortunately we lost!\n"
    elif results["result"] == "tie":
        message += "It's a tie!\n"
    message += f"Results:\n"
    message += f"    Attacks used: {results["clan"]["attacks"]}/{int(results["teamSize"])*2}\n"
    message += f"    Stars: {results["clan"]["stars"]}\n"
    message += f"    Percentage: {results["clan"]["destructionPercentage"]}\n"
    message += f"Opponent:\n"
    message += f"    Stars: {results["opponent"]["stars"]}\n"
    message += f"    Percentage: {results["opponent"]["destructionPercentage"]}\n"
    message += f"\n"
    message += f"Great job everyone!\n"
    message += f"EXP earned: {results["clan"]["expEarned"]}\n"

    channel = await client.fetch_channel(CHANNEL_ID)
    await channel.send(message)


TAG = True

async def post_prep_start():
    message = ""
    message += f":shield::crossed_swords::shield::crossed_swords::shield:\n"
    message += f"Attention honorable citizens!\n"
    message += f"Despite our diligent diplomatic efforts, war has been declared against {current_war_information.opponent_name}!\n"
    message += f"The military command has selected the following generals to lead the assault:\n"
    for participant in current_war_information.participants:
        if participant in coc_name_to_discord_id and TAG:
            message += f"    {participant} (<@{coc_name_to_discord_id[participant]}>)\n"
            continue
        message += f"    {participant}\n"
    message += f"As is tradition, the most ferocious warriors will be rewarded with the [Berserker Role] medal!\n"
    message += f"Do not be afraid dear citizens for these veterans have proven themselves to be worthy of defending our great state and will stop the enemy's advance in their tracks!\n"
    message += f"The war will commence on {current_war_information.start_time} (CET)!\n"

    channel = await client.fetch_channel(CHANNEL_ID)
    await channel.send(message)

async def post_fight_start():
    message = ""
    message += f":shield::crossed_swords::shield::crossed_swords::shield:\n"
    message += f"Attention honorable citizens!\n"
    message += f"The war day against {current_war_information.opponent_name} has begun!\n"
    message += f"May the gods of war be with us!\n"
    message += f"Remember to use both of your attacks and to coordinate with your fellow warriors!\n"
    message += f"We have until {current_war_information.end_time} (CET) to secure victory!\n"

    channel = await client.fetch_channel(CHANNEL_ID)
    await channel.send(message)

async def run():
    global current_war_information

    if not current_war_information:
        current_war_information = fetch_current_war()

    if not current_war_information:
        return

    if current_war_information.has_ended():
        if not current_war_information.posted_results:
            await post_war_results()
            print("Posted Results")
            current_war_information.posted_results = True
            current_war_information = None
            return
        
    if current_war_information.is_upcoming():
        if not current_war_information.posted_prep_start:
            await post_prep_start()
            print("Posted Prep Start")
            current_war_information.posted_prep_start = True
            return
    
    if current_war_information.has_started() and not current_war_information.has_ended():
        if not current_war_information.posted_fight_start:
            await post_fight_start()
            print("Posted Fight Start")
            current_war_information.posted_fight_start = True
            return

    

@tasks.loop(seconds=60)
async def job_loop():
    await run()
    print("sleeping for 60 seconds")

client.run(BOT_TOKEN)