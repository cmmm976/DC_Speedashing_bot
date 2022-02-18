import discord
from utils import default
from discord.ext import commands
import srcomapi, srcomapi.datatypes as dt
import datetime

class Discord_Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()        

    @commands.command()
    @commands.guild_only()
    async def runner(self, ctx, *, user):
        """ Get user information"""
        user = user or ctx.author

        """Get runner infos from SRC API"""
        
        runner_PBs = get_runs(user)

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

    @commands.command()
    @commands.guild_only()
    async def givemeroles(self, ctx, user : discord.Member = None):
        user = user or ctx.author

        runner_PBs = get_runs(user)

        has_Dead_Cells_runs = len(runner_PBs) > 0

        if not has_Dead_Cells_runs:
            raise commands.errors.UserInputError("You don't have any verified Dead Cells run :pensive:\n"
                                                 "Go show them what you've got !")

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

        threshold_roles = {"Legend": False, "Lightspeed IRL": False, "Go Fast Club": False}
        wr_roles = {"Any% WR": False}

        for category in thresholds:
            for role in threshold_roles:
                if threshold_roles[role] != True:
                    try:
                        threshold_roles[role] = simplified_PBs[category]["Time"] < thresholds[category][role]
                    except KeyError:
                        continue 
        
        roles = []
        
        for role in threshold_roles:
            roles = [discord.utils.get(ctx.guild.roles, name=role) for role in threshold_roles if threshold_roles[role]]

        print(roles)
        
        for role in roles:
            await user.add_roles(role)

        await ctx.send("Roles added successfully.")
    
    @commands.command()
    @commands.guild_only()
    async def copypasta(self, ctx):
        await ctx.send(content="i enjoy resetting 5000 times because this shit game didnt give me the level layout i wanted forcing to to try again until i finally get the perfect combination of everything i need, only to fuck up the run purely because my brain just couldnt resist the urge to go the wrong way in sepulcher. you know how frustrating this shit is? 'if i didnt get the key, that would have been sub 4' 'i got the first door, it was so close' like please and thank you ffs, lets not talk about passing 1/10 runs because pq is usually slow, just how many runs die to ramparts, the terrible level layout of stilt and trying to find sepulcher before you have to reset because it took you too long to do it, and sep which ive talked about, there are so many times sub 4 was literally there for me but i didnt get it. that is the most frustrating part - just how many runs ive thrown away to the very end of sepulcher, thats literally why i keep trying (because i know i can do it) but i have 0 patience anymore, i just want this to be over soon")



def setup(bot):
    bot.add_cog(Discord_Info(bot))
    
def sort_embeddings(embeddings, nb_categories):
    for i in range(nb_categories):
        temp_value = embeddings.pop(nb_categories+i)
        embeddings.insert(2*i+1,temp_value)

    for i in range(nb_categories):
        temp_value = embeddings.pop(nb_categories*2+i)
        embeddings.insert(3*i+2,temp_value)

def get_runs(runner):
    api = srcomapi.SpeedrunCom(); api.debug = 1

    try:
        runner_id =  api.get("users?lookup={}".format(runner))[0]['id']
    except IndexError:
        raise commands.errors.UserInputError("I haven't found this runner :pensive:\n"
                                            "Make sure you haven't mispelled their SRC username."
                                            )

    raw_PBs = api.get("users/{}/personal-bests?embed=category".format(runner_id))
    runner_PBs = {}
    for pb in raw_PBs:
        game_is_main_dead_cells = pb['run']['game'] == 'nd2ee5ed'
        game_is_extension_dead_cells = pb['run']['game'] == 'pdvzlp96'
        game_is_not_dead_cells = not game_is_main_dead_cells and not game_is_extension_dead_cells  
        
        if game_is_not_dead_cells:
            continue 
        
        category = dt.Category(api, data=pb['category']['data']).name
        misc_category = category in ["4BC (obsolete)","Any% (Early Access)", "Fresh File (Early Access)", "Any% Seeded (obsolete)"]
        
        seeded = False
        if game_is_main_dead_cells:
            
            if category == "Fresh File":
                patch_is_21_and_higher = pb['run']['values']['6njzm5pl'] == 'mln9x50q'
                category += " (2.1+)" if patch_is_21_and_higher else " (<2.1)"
            
            elif category == "5BC":
                patch_is_23_and_higher = pb['run']['values']['ylp7pkrl'] == 'p12p7j4q'
                category += " (2.3+)" if patch_is_23_and_higher else " (<2.3)"
            
            seeded = pb['run']['values']['e8m661ql'] == 'p12j3x4q'
        
        if not game_is_main_dead_cells and len(pb['run']['values']) > 0:
            seeded = pb['run']['values']['yn2wwp2n'] == 'klrknyo1'
        
        if seeded and not misc_category:
            runner_PBs[category + " (Seeded)"] = pb
        elif not seeded and not misc_category:
            runner_PBs[category] = pb
    
    return runner_PBs