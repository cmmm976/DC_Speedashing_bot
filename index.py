import os
import discord

from utils import default
from utils.data import Bot, HelpFormat
from discord.ext import tasks
from utils.src import get_new_runs
import json


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

@tasks.loop(seconds=10)
async def post_new_runs():
    new_runs_channel = bot.get_channel(931584454156230687)

    newest_run = ''
    with open('test.json') as f:
        file = json.load(f)
        newest_run = file["newest_run"]

    new_call = get_new_runs()
    
    if  new_call != newest_run:
        print("New run !")
        newest_run = new_call
        with open('newest.json', 'w') as outfile:
            json.dump({"newest_run": newest_run}, outfile)
        
        embed_run = discord.Embed.from_dict(dict(fields=[{"name": key, "value": newest_run[key], "inline": True} for key in newest_run]))

        runner_is_in_server = discord.utils.get(new_runs_channel.guild.members, name=newest_run["Runner"]) != None
        
        if runner_is_in_server:
            await new_runs_channel.send(
                "**A new run has been verified !**\n"
                "GG {} for PB ! :partying_face:".format(discord.utils.get(new_runs_channel.guild.members, name=newest_run["Runner"])), embed=embed_run
            )
        else:
            await new_runs_channel.send(
                "**A new run has been verified !**\n"
                "GG **{}** for PB ! :partying_face:".format(newest_run["Runner"]), embed=embed_run
            )
            
        await new_runs_channel.send(newest_run["Video Link"])

    

@post_new_runs.before_loop
async def before_post_new_runs():
    await bot.wait_until_ready()
    print("Ready to post new runs")

post_new_runs.start()

try:
    bot.run(config["token"])
except Exception as e:
    print(f"Error when logging in: {e}")
