
from datetime import datetime
from enum import Enum


class War_information:
    def __init__(self, opponent_name: str, start_time: str, start_time_unix: int, end_time: str, end_time_unix: int, participants: list[str]):

        self.opponent_name = opponent_name
        self.start_time = start_time
        self.start_time_unix = start_time_unix
        self.end_time = end_time
        self.end_time_unix = end_time_unix
        self.participants = participants

        self.posted_prep_start = False
        self.posted_fight_start = False
        self.posted_results = False

    def print(self):
        print("-- WAR INFORMATION --")
        print(f"Opponent: {self.opponent_name}")
        print(f"Start Time: {self.start_time}")
        print(f"End Time: {self.end_time}")
        print(f"Participants: {self.participants}")

    def is_upcoming(self):
        return self.start_time_unix > int(datetime.now().timestamp())
    
    def has_started(self):
        return self.start_time_unix < int(datetime.now().timestamp())

    def has_ended(self):
        return self.end_time_unix < int(datetime.now().timestamp())
    
    def is_about_to_end(self): # 5 sec
        return self.end_time_unix - int(datetime.now().timestamp()) < 5
  
    
def demo_PREP_war() -> War_information:
    return War_information("Demo Opponent", "02. July 2027 09:46:40", 1726512834, "03. July 2027 09:46:40", 1726599234, ["Player 1", "Player 2", "Player 3"])

def demo_OVER_war() -> War_information:
    return War_information("Demo Opponent", "28. February 2021 13:13:20", 1614514400, "29. February 2021 13:13:20", 1614600800, ["Player 1", "Player 2", "Player 3"])

def demo_FIGHT_war() -> War_information:
    return War_information("Demo Opponent", "01. January 1990 01:00:00", 50000, "01. January 2110 01:00:00", 100000000000, ["Player 1", "Player 2", "Player 3"])