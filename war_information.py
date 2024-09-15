
from datetime import datetime
from enum import Enum
import time

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
    return War_information("Demo Opponent", "tomorrow", int(time.time()) + 86400, "day after tomorrow", int(time.time()) + 86400 + 86400, ["Player 1", "Player 2", "Player 3"])

def demo_OVER_war() -> War_information:
    return War_information("Demo Opponent", "day before yesterday", int(time.time()) - 86400 - 86400, "yesterday", int(time.time()) - 86400, ["Player 1", "Player 2", "Player 3"])

def demo_FIGHT_war() -> War_information:
    return War_information("Demo Opponent", "yesterday", int(time.time()) - 86400, "tomorrow", int(time.time()) + 86400, ["Player 1", "Player 2", "Player 3"])