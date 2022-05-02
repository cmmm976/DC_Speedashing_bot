import os
import discord
import json
from time import sleep
from datetime import datetime

from utils import default
from utils.data import Bot, HelpFormat
from discord.ext import tasks
from utils.src import get_new_runs, check_if_streaming

from twitchAPI.twitch import Twitch


config = default.config()
print("Logging in...")

bot = Bot(
    command_prefix=config["prefix"], prefix=config["prefix"],
    owner_ids=config["owners"], command_attrs=dict(hidden=True), help_command=HelpFormat(),
    allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False),
    intents=discord.Intents(  # kwargs found at https://discordpy.readthedocs.io/en/latest/api.html?highlight=intents#discord.Intents
        guilds=True, members=True, messages=True, reactions=True, presences=True, message_content=True
    )
)

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

@tasks.loop(seconds=60)
async def post_new_runs():
    new_runs_channel = bot.get_channel(944573175050690590)

    newest_run = ''
    with open('data/newest_run.json', "r") as f:
        print("Opening newest_run.json !")
        file = json.load(f)
        newest_run = file["newest_run"]

    new_call = get_new_runs()
    
    if  new_call != newest_run:
        print("New run !")
        newest_run = new_call
        with open('data/newest_run.json', 'w') as outfile:
            print("Dumping newest run!")
            json.dump({"newest_run": newest_run}, outfile)
        
        embed_run = discord.Embed.from_dict(dict(fields=[{"name": key, "value": newest_run[key], "inline": True} for key in newest_run]))

        runner_is_in_server = discord.utils.get(new_runs_channel.guild.members, name=newest_run["Runner"]) != None

        runner_discord_user = discord.utils.get(new_runs_channel.guild.members, name=newest_run["Runner"])

        #checking if PB already posted
        async for message in new_runs_channel.history(limit=1):
            if runner_discord_user.mention in message.content: #if already posting, we're breaking from function (do nothing)
                print("PB already posted, leaving.")
                break
            
            if runner_is_in_server:
                await new_runs_channel.send(
                    "**A new run has been verified !**\n"
                    "GG **<@{}>** for PB ! :partying_face:".format(runner_discord_user.id), embed=embed_run
                )
            else:
                await new_runs_channel.send(
                    "**A new run has been verified !**\n"
                    "GG **{}** for PB ! :partying_face:".format(newest_run["Runner"]), embed=embed_run
                )
                
            await new_runs_channel.send(newest_run["Video Link"])

@tasks.loop(seconds=10)
async def twitch_live_notifs():
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    
    twitch_api = Twitch(CLIENT_ID, CLIENT_SECRET)

    with open("data/streamers.json", "r", encoding="UTF-8") as f:
        streamers = json.loads(f.read())

    if streamers is not None:
            # Gets guild, 'twitch streams' channel, and streaming role.
            DC_SPEEDASHING_GUILD = bot.get_guild(386680192615055361)
            STREAMS_CHANNEL = bot.get_channel(386680735374901249)
            STREAMS_ROLE = discord.utils.get(DC_SPEEDASHING_GUILD.roles, name="Streaming")

            # Loops through the json and gets the key,value which in this case is the user_id and twitch_name of
            # every item in the json.
            for user_id, twitch_name in streamers.items():
                print("checking" + " " + str(twitch_name))
                # Takes the given twitch_name and checks it using the check_if_streaming function to see if they're live.
                # Returns either true or false.
                user_live, stream_data = check_if_streaming(twitch_api, twitch_name)

                


                # Gets the user using the collected user_id in the json
                user = bot.get_user(int(user_id))
                
                #Gets game of the stream
                try:
                    game = stream_data["data"][0]["game_name"]
                except IndexError:
                    game = None

                # Makes sure they're live and streaming Dead Cells
                if user_live and game == "Dead Cells":
                    # Checks to see if the live message has already been sent.
                    async for message in STREAMS_CHANNEL.history(limit=200):
                        twitch_embed = discord.Embed(
                                title=f":red_circle: **LIVE** :red_circle:\n{stream_data['data'][0]['title']}",
                                color=0xac1efb,
                                url=f'\nhttps://www.twitch.tv/{twitch_name}'
                            )
                        try:
                            twitch_embed.set_image(url = twitch_api.get_streams(user_login=twitch_name)["data"][0]["thumbnail_url"].split("-{width}")[0]+".jpg")
                        except IndexError:
                            print("Wasn't ready to post yet, trying again")
                            sleep(10)
                            twitch_embed.set_image(url = twitch_api.get_streams(user_login=twitch_name)["data"][0]["thumbnail_url"].split("-{width}")[0]+".jpg")

                        #Gets timestamp of stream start
                        stream_start = datetime.strptime(stream_data["started_at"],"%Y-%m-%dT%H:%M:%SZ").replace().timestamp()
                        #compute time after stream_start in seconds
                        time_after_stream_start = datetime.now().timestamp() - stream_start
                        
                        # If it has, break the loop (do nothing).
                        #Also check if stream starts for longer than 1 minute. 
                        # If yes, break the loop (do nothing). 
                        # Avoid spam if multiple streamers active
                        if user.mention in message.content or time_after_stream_start > 60:
                            print("Announcement already posted, leaving.")
                            break
                        # If it hasn't, assign them the streaming role and send the message.
                        else:
                            # Gets all the members in your guild.
                            async for member in DC_SPEEDASHING_GUILD.fetch_members(limit=None):
                                # If one of the id's of the members in your guild matches the one from the json and
                                # they're live, give them the streaming role.
                                if member.id == int(user_id):
                                    await member.add_roles(STREAMS_ROLE)
                            # Sends the live notification to the 'twitch streams' channel then breaks the loop.
                            await STREAMS_CHANNEL.send(
                                content = f"{user.mention} is now streaming Dead Cells! Go check it out: https://www.twitch.tv/{twitch_name}", embed=twitch_embed)
                            print(f"{user} started streaming. Sending a notification.")
                            break
                # If they aren't live do this:
                else:
                    # Gets all the members in your guild.
                    async for member in DC_SPEEDASHING_GUILD.fetch_members(limit=None):
                        # If one of the id's of the members in your guild matches the one from the json and they're not
                        # live, remove the streaming role.
                        if member.id == int(user_id):
                            await member.remove_roles(STREAMS_ROLE)
                    # Checks to see if the live notification was sent.
                    async for message in STREAMS_CHANNEL.history(limit=200):
                        # If it was, delete it.
                        if user.mention in message.content and "is now streaming" in message.content:
                            print(f"{user} stopped streaming. Removing the notification.")
                            await message.delete()
    

@post_new_runs.before_loop
async def before_post_new_runs():
    await bot.wait_until_ready()
    print("Ready to post new runs")

@twitch_live_notifs.before_loop
async def before_twitch_live_notifs():
    await bot.wait_until_ready()
    print("Ready to post Twitch live notifs")

post_new_runs.start()
twitch_live_notifs.start()

try:
    bot.run(config["token"])
except Exception as e:
    print(f"Error when logging in: {e}")
