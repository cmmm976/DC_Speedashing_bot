import discord
from io import BytesIO
from utils import default
from discord.ext import commands
import srcomapi, srcomapi.datatypes as dt
import datetime
import sys

class Discord_Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.UserInputError):
            await ctx.send(f"Runner not found :pensive: Make sure you haven't mispelled their SRC username.")

    @commands.command()
    @commands.guild_only()
    async def avatar(self, ctx, *, user: discord.Member = None):
        """ Get the avatar of you or someone else """
        user = user or ctx.author
        await ctx.send(f"Avatar to **{user.name}**\n{user.avatar.with_size(1024)}")

    @commands.command()
    @commands.guild_only()
    async def roles(self, ctx):
        """ Get all roles in current server """
        allroles = ""

        for num, role in enumerate(sorted(ctx.guild.roles, reverse=True), start=1):
            allroles += f"[{str(num).zfill(2)}] {role.id}\t{role.name}\t[ Users: {len(role.members)} ]\r\n"

        data = BytesIO(allroles.encode("utf-8"))
        await ctx.send(content=f"Roles in **{ctx.guild.name}**", file=discord.File(data, filename=f"{default.timetext('Roles')}"))

    @commands.command()
    @commands.guild_only()
    async def joinedat(self, ctx, *, user: discord.Member = None):
        """ Check when a user joined the current server """
        user = user or ctx.author

        embed = discord.Embed(colour=user.top_role.colour.value)
        embed.set_thumbnail(url=user.avatar)
        embed.description = f"**{user}** joined **{ctx.guild.name}**\n{default.date(user.joined_at, ago=True)}"
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def mods(self, ctx):
        """ Check which mods are online on current guild """
        message = ""
        all_status = {
            "online": {"users": [], "emoji": "🟢"},
            "idle": {"users": [], "emoji": "🟡"},
            "dnd": {"users": [], "emoji": "🔴"},
            "offline": {"users": [], "emoji": "⚫"}
        }

        for user in ctx.guild.members:
            user_perm = ctx.channel.permissions_for(user)
            if user_perm.kick_members or user_perm.ban_members:
                if not user.bot:
                    all_status[str(user.status)]["users"].append(f"**{user}**")

        for g in all_status:
            if all_status[g]["users"]:
                message += f"{all_status[g]['emoji']} {', '.join(all_status[g]['users'])}\n"

        await ctx.send(f"Mods in **{ctx.guild.name}**\n{message}")

    @commands.group()
    @commands.guild_only()
    async def server(self, ctx):
        """ Check info about current server """
        if ctx.invoked_subcommand is None:
            find_bots = sum(1 for member in ctx.guild.members if member.bot)

            embed = discord.Embed()

            if ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon)
            if ctx.guild.banner:
                embed.set_image(url=ctx.guild.banner.with_format("png").with_size(1024))

            embed.add_field(name="Server Name", value=ctx.guild.name, inline=True)
            embed.add_field(name="Server ID", value=ctx.guild.id, inline=True)
            embed.add_field(name="Members", value=ctx.guild.member_count, inline=True)
            embed.add_field(name="Bots", value=find_bots, inline=True)
            embed.add_field(name="Owner", value=ctx.guild.owner, inline=True)
            embed.add_field(name="Region", value=ctx.guild.region, inline=True)
            embed.add_field(name="Created", value=default.date(ctx.guild.created_at, ago=True), inline=True)
            await ctx.send(content=f"ℹ Information about **{ctx.guild.name}**", embed=embed)

    @server.command(name="avatar", aliases=["icon"])
    async def server_avatar(self, ctx):
        """ Get the current server icon """
        if not ctx.guild.icon:
            return await ctx.send("This server does not have a avatar...")
        await ctx.send(f"Avatar of **{ctx.guild.name}**\n{ctx.guild.icon}")

    @server.command(name="banner")
    async def server_banner(self, ctx):
        """ Get the current banner image """
        if not ctx.guild.banner:
            return await ctx.send("This server does not have a banner...")
        await ctx.send(f"Banner of **{ctx.guild.name}**\n{ctx.guild.banner.with_format('png')}")

    @commands.command()
    @commands.guild_only()
    async def user(self, ctx, *, user: discord.Member = None):
        """ Get user information """
        user = user or ctx.author

        show_roles = ", ".join(
            [f"<@&{x.id}>" for x in sorted(user.roles, key=lambda x: x.position, reverse=True) if x.id != ctx.guild.default_role.id]
        ) if len(user.roles) > 1 else "None"

        embed = discord.Embed(colour=user.top_role.colour.value)
        embed.set_thumbnail(url=user.avatar)

        embed.add_field(name="Full name", value=user, inline=True)
        embed.add_field(name="Nickname", value=user.nick if hasattr(user, "nick") else "None", inline=True)
        embed.add_field(name="Account created", value=default.date(user.created_at, ago=True), inline=True)
        embed.add_field(name="Joined this server", value=default.date(user.joined_at, ago=True), inline=True)
        embed.add_field(name="Roles", value=show_roles, inline=False)

        await ctx.send(content=f"ℹ About **{user.id}**", embed=embed)

    @commands.command()
    @commands.guild_only()
    async def runner(self, ctx, *, user):
        """ Get user information"""
        user = user or ctx.author

        """Get runner infos from SRC API"""
        
        runner_PBs = get_runs(user)
        
        embeddings = dict(fields=[])
        embeddings["fields"].extend([{"name": "Category", "value": x, "inline": True} for x in runner_PBs.keys()])
        embeddings["fields"].extend([{"name": "Rank", "value": str(runner_PBs[x]["place"]), "inline": True} for x in runner_PBs.keys()])
        embeddings["fields"].extend([{"name": "Time", "value": str(datetime.timedelta(seconds=runner_PBs[x]["run"]["times"]["primary_t"])).rstrip("000"), "inline": True} for x in runner_PBs.keys()])
        
        sort_embeddings(embeddings["fields"],len(runner_PBs.keys()))

        embed = discord.Embed.from_dict(embeddings)
        

        await ctx.send(content=f"ℹ **{user}** speedrun profile", embed=embed)

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
        raise commands.errors.UserInputError("Runner not found")
   
  
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