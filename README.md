# Dead Cells Speedashing discord bot

A bot for the Dead Cells Speedrunning discord bot created from [AlexFlipnote](https://github.com/AlexFlipnote/) [discord_bot.py](https://github.com/AlexFlipnote/discord_bot.py)

**Stack : Python 3.6+, Docker, OVH Bare Metal Cloud**

# Setup
 * Clone the repo : `git clone https://github.com/cmmm976/DC_Speedashing_bot`
 * Create, configure your bot and and add a config.json file ([readme](https://github.com/AlexFlipnote/discord_bot.py#readme))
    * Be sure to enable all the Privileged Gateway Intents
 * Install the requirements `pip install -r requirements.txt`

# Run it

First, invite your bot with this link : https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=275146411072&scope=bot with CLIENT_ID your bot client ID

## Locally
Open a terminal, navigate to the repo folder and launch index.py : `python index.py`

## On a Docker container
[Docker](https://docs.docker.com/install/) allows you to run the bot 24/7.
```# Build and run the Dockerfile
docker-compose up -d --build

# Tips on common commands
docker-compose <command>
  ps      Check if bot is online or not (list)
  down    Shut down the bot
  reboot  Reboot the bot without shutting it down or rebuilding
  logs    Check the logs made by the bot.
```
# Features
 * Posts new verified runs in a dedicated channel
 * Posts a runner PB through the !runner command
 * Posts a random copypasta through the !copypasta command
 * Runs 24/7 in a Cloud-hosted container
 
