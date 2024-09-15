Running this Script requires you to create a file called "credentials.py".

This is the template for credentials.py:
```Python

# Fill in your Clash of Clans API key here.
# Make sure it allows the IP-Adress of the
# device this script is running on
coc_api_key = ""

# Fill in your Clash of Clans Clan Tag here.
# Replace the "#" with "%23"
clan_tag = "%23..."

# Fill in the Token for your Discord Bot
DISCORD_BOT_TOKEN = ""

# Fill in the Discord Channel ID you want
# the bot to send messages to.
# Make sure the Bot has access to the Channel
DISCORD_CHANNEL_ID = "1284093507488841759"

# This is a Dictionary where you can add
# the Discord IDs of every Clan Member
# This will allow the Bot to tag them 
coc_name_to_discord_id = {
    "coc_name_1": "discord_user_id_1",
    "coc_name_2": "discord_user_id_2"
    ...
}

```

Before being able to run the bot you need to install some packages:
```Bash
pip install -r requirements.txt
```


Then you can run the bot like this:
```Bash
python main.py
```
