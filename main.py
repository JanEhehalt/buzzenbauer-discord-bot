import requests
from datetime import datetime, timezone
from time import sleep
import pytz
import discord
from discord import *
from discord.ext import tasks

from war_information import War_information, demo_PREP_war, demo_FIGHT_war, demo_OVER_war
from credentials import coc_name_to_discord_id
from credentials import coc_api_key, clan_tag
from credentials import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID
from credentials import DISCORD_GUILD_ROSTER_CHANNEL_ID

# use this for restarting the prod Bot
SKIP_FIRST_MESSAGE = True
TAG_WAR_PARTICIPANTS = True
CREATE_EVENT = True
BOT_TOKEN = DISCORD_BOT_TOKEN
CHANNEL_ID = DISCORD_CHANNEL_ID



current_war_information = None

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True 

client = discord.Client(intents=intents)

def fetch_current_war() -> War_information:
    headers = {"Authorization": f"Bearer {coc_api_key}"}
    currentwar = f"https://api.clashofclans.com/v1/clans/{clan_tag}/currentwar"
    data = requests.get(currentwar, headers=headers).json()

    if data.get("state") == "inWar" or data.get("state") == "preparation":
        new_opponent = data.get("opponent").get("name")
        
        new_start_time_raw = data.get("startTime")
        new_start_time_raw = datetime.strptime(new_start_time_raw, "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=timezone.utc)
        germany_timezone = pytz.timezone('Europe/Berlin') 
        new_start_time_local = new_start_time_raw.astimezone(germany_timezone)
        new_start_time = new_start_time_local.strftime("%d. %B %Y %H:%M:%S")
        new_end_time_raw = data.get("endTime")
        new_end_time_raw = datetime.strptime(new_end_time_raw, "%Y%m%dT%H%M%S.%fZ").replace(tzinfo=timezone.utc)

        new_end_time_local = new_end_time_raw.astimezone(germany_timezone)
        new_end_time = new_end_time_local.strftime("%d. %B %Y %H:%M:%S")

        participants = []
        for member in data.get("clan").get("members"):
            participants.append(member.get("name"))
        
        return War_information(new_opponent, new_start_time, int(new_start_time_raw.timestamp()), new_end_time, int(new_end_time_raw.timestamp()), participants)
    return None

def fetch_results():
    headers = {"Authorization": f"Bearer {coc_api_key}"}
    warlog = f"https://api.clashofclans.com/v1/clans/{clan_tag}/warlog?limit=1"
    return requests.get(warlog, headers=headers).json()

async def post_war_results(results):
    if SKIP_FIRST_MESSAGE:
        SKIP_FIRST_MESSAGE = False
        return
    message = ""
    message += f":shield::crossed_swords::shield::crossed_swords::shield:\n"
    message += f"War against {results['opponent']['name']} ({results['opponent']['tag']}) has ended!\n"
    if results['result'] == "win":
        message += "We won!\n"
    elif results['result'] == "lose":
        message += "Unfortunately we lost!\n"
    elif results['result'] == "tie":
        message += "It's a tie!\n"
    message += f"Results:\n"
    message += f"    Attacks used: {results['clan']['attacks']}/{int(results['teamSize'])*2}\n"
    message += f"    Stars: {results['clan']['stars']}\n"
    message += f"    Percentage: {results['clan']['destructionPercentage']}\n"
    message += f"Opponent:\n"
    message += f"    Stars: {results['opponent']['stars']}\n"
    message += f"    Percentage: {results['opponent']['destructionPercentage']}\n"
    message += f"\n"
    message += f"Great job everyone!\n"
    message += f"EXP earned: {results['clan']['expEarned']}\n"

    channel = await client.fetch_channel(CHANNEL_ID)
    await channel.send(message)

async def post_prep_start(war_information: War_information):
    if SKIP_FIRST_MESSAGE:
        SKIP_FIRST_MESSAGE = False
        return
    channel = await client.fetch_channel(CHANNEL_ID)

    message = ""
    message += f":shield::crossed_swords::shield::crossed_swords::shield:\n"
    message += f"Attention honorable citizens!\n"
    message += f"Despite our diligent diplomatic efforts, war has been declared against {war_information.opponent_name}!\n"
    message += f"The military command has selected the following generals to lead the assault:\n"
    for participant in war_information.participants:
        if participant in coc_name_to_discord_id and TAG_WAR_PARTICIPANTS:
            message += f"    {participant} (<@{coc_name_to_discord_id[participant]}>)\n"
            continue
        message += f"    {participant}\n"
    message += f"As is tradition, the most ferocious warriors will be rewarded with the [Berserker Role] medal!\n"
    message += f"Do not be afraid dear citizens for these veterans have proven themselves to be worthy of defending our great state and will stop the enemy's advance in their tracks!\n"
    message += f"The war will commence on {war_information.start_time} (CET)!\n"

    if CREATE_EVENT:
        germany_timezone = pytz.timezone('Europe/Berlin') 
        event_start_time = datetime.fromtimestamp(current_war_information.start_time_unix).astimezone(germany_timezone) 
        event_end_time = datetime.fromtimestamp(current_war_information.end_time_unix).astimezone(germany_timezone)
        event = await channel.guild.create_scheduled_event(
            name="War against " + current_war_information.opponent_name,
            start_time=event_start_time,
            end_time=event_end_time,
            description="Join the war!",
            location=f"<#{CHANNEL_ID}>",
            entity_type=EntityType.external,
            privacy_level=PrivacyLevel.guild_only
        )
        message += event.url

    await channel.send(message)

async def post_fight_start(war_information: War_information):
    if SKIP_FIRST_MESSAGE:
        SKIP_FIRST_MESSAGE = False
        return
    message = ""
    message += f":shield::crossed_swords::shield::crossed_swords::shield:\n"
    message += f"Attention honorable citizens!\n"
    message += f"The war day against {war_information.opponent_name} has begun!\n"
    message += f"May the gods of war be with us!\n"
    message += f"Remember to use both of your attacks and to coordinate with your fellow warriors!\n"
    message += f"We have until {war_information.end_time} (CET) to secure victory!\n"

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
            results = fetch_results()['items'][0]
            if results['opponent']['name'] != current_war_information.opponent_name:
                return
            await post_war_results(results)
            print("Posted Results")
            current_war_information.posted_results = True
            current_war_information = None
            return
        
    if current_war_information.is_upcoming():
        if not current_war_information.posted_prep_start:
            await post_prep_start(current_war_information)
            print("Posted Prep Start")
            current_war_information.posted_prep_start = True
            return
    
    if current_war_information.has_started() and not current_war_information.has_ended():
        if not current_war_information.posted_fight_start:
            await post_fight_start(current_war_information)
            print("Posted Fight Start")
            current_war_information.posted_fight_start = True
            return

@client.event
async def on_ready():
    print(f"Logged in as {client.user}.")
    job_loop.start()


@tasks.loop(seconds=60)
async def job_loop():
    await run()
    print("sleep")


guild_roster_message = None
current_leader = ""
current_co_leaders = []
current_elders = []
current_members = []

async def update_guild_roster():
    global guild_roster_message, current_leader, current_co_leaders, current_elders, current_members

    headers = {"Authorization": f"Bearer {coc_api_key}"}
    currentwar = f"https://api.clashofclans.com/v1/clans/{clan_tag}"
    data = requests.get(currentwar, headers=headers).json().get("memberList")

    update_necessary = False

    new_leader = ""
    for member in data:
        if member.get("role") == "leader":
            new_leader = member.get("name")
            break
    
    new_co_leaders = []
    for member in data:
        if member.get("role") == "coLeader":
            new_co_leaders.append(member.get("name"))

    new_elders = []
    for member in data:
        if member.get("role") == "admin" or member.get("role") == "elder":
            new_elders.append(member.get("name"))

    new_members = []
    for member in data:
        if member.get("role") == "member":
            new_members.append(member.get("name"))

    if  new_leader != current_leader or set(new_members) != set(current_members) or set(new_co_leaders) != set(current_co_leaders) or set(new_elders) != set(current_elders):
        update_necessary = True
        current_leader = new_leader
        current_co_leaders = new_co_leaders
        current_elders = new_elders
        current_members = new_members


    if update_necessary:
        counter = 1
        message =  f"This is our current roster:\n"
        message += f"\n"
        message += f"Our Leader:"
        message += f"  {counter}. {current_leader}\n"
        counter += 1
        message += f"\n"
        message += f"Our Co-Leaders:"
        for co_leader in current_co_leaders:
            message += f"  {counter}. {co_leader}\n"
            counter += 1
        message += f"\n"
        message += f"Our Elders:"
        for elder in current_elders:
            message += f"  {counter}. {elder}\n"
            counter += 1
        message += f"\n"
        message += f"Our Members:"
        for member in current_members:
            message += f"  {counter}. {member}\n"
            counter += 1
        message += f"\n"

        if not guild_roster_message:
            channel = await client.fetch_channel(DISCORD_GUILD_ROSTER_CHANNEL_ID)
            guild_roster_message = await channel.send(message)
        else:
            await guild_roster_message.edit(content=message)


@tasks.loop(seconds=300)
async def job_loop():
    print("updating guild roster")
    await update_guild_roster()


client.run(BOT_TOKEN)