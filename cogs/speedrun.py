import discord
from utils import default
from discord.ext import commands, tasks
from utils.src import sort_embeddings, get_PBs
import datetime
import random

class Speedrun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        
    @commands.command()
    @commands.guild_only()
    async def runner(self, ctx, *, user):
        """ Get runner personal bests"""
        user = user or ctx.author

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
        user = user or ctx.author

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
                        "Any% Warpless (Seeded)": {"Legend": 2.5*60, "Lightspeed IRL": 3*60, "Go Fast Club": 3.5*60}, 
                        "Any% Warps": {"Legend": 50, "Lightspeed IRL": 60},
                        "Fresh File (<2.1)": {"Legend": 14*60, "Lightspeed IRL": 15*60, "Go Fast Club": 17*60}, 
                        "Fresh File (2.1+)": {"Legend": 11*60, "Lightspeed IRL": 12*60, "Go Fast Club": 13*60},
                        "0-5BC Glitchless": {"Legend": 2.5*60*60, "Lightspeed IRL": 3*60*60}
                        }

            world_records = {"Any% Warpless": {"Any% WR" :1}, 
                            "Any% Warpless (Seeded)": {"Any% WR" :1},
                            "Any% Warps": {"Warps WR" :1},
                            "Fresh File (<2.1)": {"FF WR" :1},
                            "Fresh File (2.1+)": {"FF WR" :1},
                            "0-5BC Glitchless": {"0-5BC WR" :1},
                            "5BC (<2.3)": {"5BC WR" :1},
                            "5BC (2.3+)": {"5BC WR" :1},
                            "5BC No Major Glitches": {"5BC WR" :1}
                            }

            threshold_roles = {"Legend": False, "Lightspeed IRL": False, "Go Fast Club": False}
            wr_roles = {"Any% WR": False, "Warps WR": False, "FF WR": False, "5BC WR": False, "0-5BC WR": False}

            for category in thresholds:
                for role in threshold_roles:
                    if threshold_roles[role] != True:
                        try:
                            threshold_roles[role] = simplified_PBs[category]["Time"] < thresholds[category][role]
                        except KeyError:
                            continue 
            
            for category in world_records:
                for role in wr_roles:
                    if wr_roles[role] != True:
                        try:
                            wr_roles[role] = simplified_PBs[category]["Rank"] == world_records[category][role]
                        except KeyError:
                            continue 
            
            
            roles_to_remove = [discord.utils.get(ctx.guild.roles, name=role) for role in wr_roles if not wr_roles[role]]

            roles_to_append = [discord.utils.get(ctx.guild.roles, name=role) for role in threshold_roles if threshold_roles[role]]
            roles_to_append.extend([discord.utils.get(ctx.guild.roles, name=role) for role in wr_roles if wr_roles[role]])
            roles_to_append.append(discord.utils.get(ctx.guild.roles, name="Runner"))

            print(roles_to_append)
            
            for role in roles_to_append:
                await user.add_roles(role)

            for role in roles_to_remove:
                await user.remove_roles(role)

            await ctx.send("Roles updated successfully.")
    
    @commands.command(aliases=['i enjoy','c'])
    @commands.guild_only()
    async def copypasta(self, ctx):
        """Post a random Dead Cells speedrunning copypasta"""
        copypastas = ["i enjoy resetting 5000 times because this shit game didnt give me the level layout i wanted forcing to to try again until i finally get the perfect combination of everything i need, only to fuck up the run purely because my brain just couldnt resist the urge to go the wrong way in sepulcher. you know how frustrating this shit is? 'if i didnt get the key, that would have been sub 4' 'i got the first door, it was so close' like please and thank you ffs, lets not talk about passing 1/10 runs because pq is usually slow, just how many runs die to ramparts, the terrible level layout of stilt and trying to find sepulcher before you have to reset because it took you too long to do it, and sep which ive talked about, there are so many times sub 4 was literally there for me but i didnt get it. that is the most frustrating part - just how many runs ive thrown away to the very end of sepulcher, thats literally why i keep trying (because i know i can do it) but i have 0 patience anymore, i just want this to be over soon","This game's a fucking joke. I boot up trying to get a good old 5BC NMG speedrun going and pick out my build, with Barbed Tips for some optimal cheese. Doing the run and guess what? 53 arrows with a Hokuto's buff is doing jack shit to the boss. I'm still on WR pace though so I keep going until Astro, where 3 librarians gang up and destroy the few little bits of sanity I have trying to survive that dogshit biome with a mob composition hand-crafted to make speedrunners suffer the most scientifically possible. Astro's the worst god damn biome and there's no way that around 300k DPS takes 2 god damn minutes to kill HotK."]
        await ctx.send(content=random.choice(copypastas))


def setup(bot):
    bot.add_cog(Speedrun(bot))
    

