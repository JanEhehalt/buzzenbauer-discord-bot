import requests
from credentials import coc_api_key, clan_tag
from datetime import datetime


headers = {"Authorization": f"Bearer {coc_api_key}"}

currentwar = f"https://api.clashofclans.com/v1/clans/{clan_tag}/currentwar"

currentwar_opponent = None

if not currentwar_opponent:
    data = requests.get(currentwar, headers=headers).json()
    new_opponent = requests.get(currentwar, headers=headers).json().get("opponent").get("name")
    
    new_start_time_raw= requests.get(currentwar, headers=headers).json().get("startTime")
    new_start_time_raw = datetime.strptime(new_start_time_raw, "%Y%m%dT%H%M%S.%fZ")
    new_start_time = new_start_time_raw.strftime("%d. %B %Y %H:%M:%S")

    participants = []
    for member in data.get("clan").get("members"):
        participants.append(member.get("name"))
    
    print(f"A new CLAN WAR has begun!")
    print(f"We will face the pathetic fools who call themselves {new_opponent}.")
    print(f"The war will be starting at {new_start_time}.")
    print(f"Make sure to fill out Clan Castles!")
    print("These are our designated WARRIORS:")
    for participant in participants:
        print("    " + participant)
    print("Good Luck and Clash On!")