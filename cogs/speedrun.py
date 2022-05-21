import discord
import datetime
import random
import json

from utils import default
from discord.ext import commands, tasks
from utils.src import sort_embeddings, get_PBs, get_category_WRs, VALUES, VARIABLES, CATEGORIES, SUB_CATEGORIES


class Speedrun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        
    @commands.command()
    @commands.guild_only()
    async def runner(self, ctx, *, user):
        """ Get runner personal bests"""
        user = user or user

        """Get runner infos from SRC API"""
        
        runner_PBs = get_PBs(user)

        has_Dead_Cells_runs = len(runner_PBs) > 0

        if not has_Dead_Cells_runs:
            raise commands.errors.UserInputError(f"This runner doesn't have any Dead Cells PB. Good for them !")

        embeddings = dict(fields=[])
        embeddings["fields"].extend([{"name": "Category", "value": x, "inline": True} for x in runner_PBs.keys()])
        embeddings["fields"].extend([{"name": "Rank", "value": str(runner_PBs[x]["place"]), "inline": True} for x in runner_PBs.keys()])
        embeddings["fields"].extend([{"name": "Time", "value": str(datetime.timedelta(seconds=runner_PBs[x]["run"]["times"]["primary_t"])).rstrip("000"), "inline": True} for x in runner_PBs.keys()])
        
        sort_embeddings(embeddings["fields"],len(runner_PBs.keys()))

        embed = discord.Embed.from_dict(embeddings)

        await ctx.send(content=f"ℹ **{user}** speedrun profile", embed=embed)

    @commands.command(aliases=['roles'])
    @commands.guild_only()
    async def givemeroles(self, ctx, user : discord.Member = None):
        """Gives you the accurate roles based on your personal bests (see #role-pls for requirements)"""
        user = user or user

        async with ctx.channel.typing():
            runner_PBs = get_PBs(user)

            has_Dead_Cells_runs = len(runner_PBs) > 0

            if not has_Dead_Cells_runs:
                raise commands.errors.UserInputError("You don't have any verified Dead Cells run :pensive:\n"
                                                    "If I'm wrong, that means speedrun.com API is stupid, sorry. :shrug:\n"
                                                    "You can make your Discord username exactly matches your SRC one to solve this issue.")

            simplified_PBs = {}
            for category in runner_PBs.keys():
                simplified_PBs[category] = {"Time": runner_PBs[category]["run"]["times"]["primary_t"], "Rank": runner_PBs[category]["place"]}

            thresholds = {"Any% Warpless": {"Legend": 4*60, "Lightspeed IRL": 5*60, "Go Fast Club": 6*60}, 
                        "Any% Warpless (Seeded)": {"Legend": (2+(20/60))*60, "Lightspeed IRL": 3*60, "Go Fast Club": 3.5*60}, 
                        "Any% Warps (+60 FPS)": {"Legend": 35, "Lightspeed IRL": 45, "Go Fast Club": 50},
                        "Any% Warps (+60 FPS) (Seeded)": {"Legend": 25, "Lightspeed IRL": 30, "Go Fast Club": 35},
                        "Fresh File (<2.1)": {"Legend": 14*60, "Lightspeed IRL": 15*60, "Go Fast Club": 17*60}, 
                        "Fresh File (2.1+)": {"Legend": 10*60, "Lightspeed IRL": 11*60, "Go Fast Club": 12*60},
                        "0-5BC Glitchless": {"Legend": 2.5*60*60, "Lightspeed IRL": 3*60*60, "Go Fast Club": 3.75*60*60},
                        "5BC (<2.5)": {"Legend": 9*60, "Lightspeed IRL": 10*60, "Lightspeed IRL": 11*60},
                        "5BC (2.5+)": {"Legend": 10*60, "Lightspeed IRL": 11*60, "Lightspeed IRL": 13*60},
                        "5BC (<2.5) (NMG)": {"Legend": 20*60},
                        "5BC (2.5+) (NMG)": {"Legend": 18*60}
                        }

            world_records = {"Any% Warpless": {"Any% WR" :1}, 
                            "Any% Warpless (Seeded)": {"Any% WR" :1},
                            "Any% Warps (60+ FPS)": {"Warps WR" :1},
                            "Any% Warps (60+ FPS) (Seeded)": {"Warps WR" :1},
                            "Fresh File (<2.1)": {"FF WR" :1},
                            "Fresh File (2.1+)": {"FF WR" :1},
                            "0-5BC Glitchless": {"0-5BC WR" :1},
                            "5BC (<2.5)": {"5BC WR" :1},
                            "5BC (2.5+)": {"5BC WR" :1},
                            "All Bosses": {"All Bosses WR" :1},
                            "Boss Rush (QatS)": {"Boss Rush WR" :1},
                            "Boss Rush (Fatal Falls)": {"Boss Rush WR" :1},
                            "All Runes": {"All Runes WR" :1},
                            "Reverse Rune Order": {"Reverse Rune Order WR" :1},
                            "Cursed Sword Glitchless": {"Cursed WR" :1},
                            }

            
            threshold_roles = {"Legend": False, "Lightspeed IRL": False, "Go Fast Club": False}
            wr_roles = {list(x.keys())[0]:False for x in world_records.values()}
            nb_thresholds_meet = {"Legend": 0, "Lightspeed IRL": 0, "Go Fast Club": 0}
            nb_thresholds_needed = {"Legend": 2, "Lightspeed IRL": 1, "Go Fast Club": 1}

            for category in thresholds:
                for role in nb_thresholds_meet:
                        try:
                            nb_thresholds_meet[role] += 1 if simplified_PBs[category]["Time"] < thresholds[category][role] else 0
                            print(category, simplified_PBs[category]["Time"], simplified_PBs[category]["Time"] < thresholds[category][role])
                        except KeyError:
                            continue
            
            for role in nb_thresholds_meet:
                threshold_roles[role] = nb_thresholds_meet[role] >= nb_thresholds_needed[role]
                print(role, nb_thresholds_meet[role], nb_thresholds_meet[role] >= nb_thresholds_needed[role])

            for category in world_records:
                for role in wr_roles:
                    if wr_roles[role] != True:
                        try:
                            wr_roles[role] = simplified_PBs[category]["Rank"] == world_records[category][role]
                        except KeyError:
                            continue 
            
            roles_to_remove = [discord.utils.get(ctx.guild.roles, name=role) for role in wr_roles if not wr_roles[role]]
            roles_to_remove.extend([discord.utils.get(ctx.guild.roles, name=role) for role in threshold_roles if not threshold_roles[role]])

            roles_to_append = [discord.utils.get(ctx.guild.roles, name=role) for role in threshold_roles if threshold_roles[role]]
            roles_to_append.extend([discord.utils.get(ctx.guild.roles, name=role) for role in wr_roles if wr_roles[role]])
            roles_to_append.append(discord.utils.get(ctx.guild.roles, name="Runner"))

            print(roles_to_append)
            
            for role in roles_to_append:
                await user.add_roles(role)

            for role in roles_to_remove:
                await user.remove_roles(role)

            await ctx.send("Roles updated successfully.")
    
    @commands.command(aliases=['i enjoy', 'copypastas'])
    @commands.guild_only()
    async def copypasta(self, ctx):
        """Posts a random Dead Cells speedrunning copypasta"""
        copypastas = None
        with open("data/copypastas.txt", "r") as f:
            copypastas = f.readlines()
            
        await ctx.send(content=random.choice(copypastas))
    
    @commands.command(aliases=["world record", "wrs"])
    @commands.guild_only()
    async def wr(self, ctx, category):
        """Posts the world records of a category"""

        world_records = get_category_WRs(category)
        print(world_records)

        await ctx.send(content="**{} World records**".format(category))

        for wr in world_records:
            embeddings = dict(fields=[])
            for name, value in wr.items():
                embeddings["fields"].append({"name": name, "value": str(value), "inline": False})

            embed = discord.Embed.from_dict(embeddings)
            embed.set_thumbnail(url="https://discord.com/assets/f3e307960b1c81de130c429034802618.svg")
            await ctx.send(embed=embed)


    @commands.command(aliases=["exposed", "casuls"])
    async def casul(self, ctx):
        """Posts a random screenshot of casuls reacting to a Dead Cells speedrun"""
        casuls = None
        with open("data/casuls.txt", "r") as f:
            casuls = f.readlines()
        
        await ctx.send(content=random.choice(casuls))

   
    @commands.command(aliases=["live_notifs"])
    async def add_twitch(self, ctx, twitch_name, user : discord.Member = None):
        """Command to make the bot knows your Twitch so it can announce your streams!"""
        user = user or ctx.author

        # Opens and reads the json file.
        with open('data/streamers.json', 'r') as file:
            streamers = json.loads(file.read())
        
        # Gets the users id that called the command or the user in arguement
        user_id = str(user.id)

        print(user_id)

        if user_id not in streamers:
            # Assigns their given twitch_name to their discord id and adds it to the streamers.json.
            streamers[user_id] = twitch_name
            # Adds the changes we made to the json file.
            with open('data/streamers.json', 'w') as file:
                file.write(json.dumps(streamers))
            # Tells the user it worked.
            await ctx.send(f"Added {twitch_name} for {user} to the notifications list.")
        else:
            await ctx.send(f"{user}'s Twitch is already in the notifications list.")


def setup(bot):
    bot.add_cog(Speedrun(bot))
    

