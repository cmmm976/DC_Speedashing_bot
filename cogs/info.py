import time
import discord
import psutil
import os

from discord.ext import commands
from utils import default, http


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.process = psutil.Process(os.getpid())

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        message = await ctx.send("🏓 Pong")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"🏓 WS: {before_ws}ms  |  REST: {int(ping)}ms")

    @commands.command(aliases=["joinme", "join", "botinvite"])
    async def invite(self, ctx):
        """ Invite me to your server """
        await ctx.send(f"**{ctx.author.name}**, use this URL to invite me\n<{discord.utils.oauth_url(self.bot.user.id)}>")

    @commands.command()
    async def source(self, ctx):
        """ Check out my source code <3 """
        await ctx.send(f"**{ctx.bot.user}** is powered by this source code:\nhttps://github.com/cmmm976/DC_Speedashing_bot")


    @commands.command(aliases=["info", "stats", "status"])
    async def about(self, ctx):
        """ About the bot """
        ramUsage = self.process.memory_full_info().rss / 1024**2
        avgmembers = sum(g.member_count for g in self.bot.guilds) / len(self.bot.guilds)

        embedColour = discord.Embed.Empty
        if hasattr(ctx, "guild") and ctx.guild is not None:
            embedColour = ctx.me.top_role.colour

        embed = discord.Embed(colour=embedColour)
        embed.set_thumbnail(url=ctx.bot.user.avatar)
        embed.add_field(name="Last boot", value=default.date(self.bot.uptime, ago=True))
        embed.add_field(
            name=f"Developer{'' if len(self.config['owners']) == 1 else 's'}",
            value=", ".join([str(self.bot.get_user(x)) for x in self.config["owners"]])
        )
        embed.add_field(name="Library", value="Pycord")
        embed.add_field(name="Servers", value=f"{len(ctx.bot.guilds)} ( avg: {avgmembers:,.2f} users/server )")
        embed.add_field(name="Commands loaded", value=len([x.name for x in self.bot.commands]))
        embed.add_field(name="RAM", value=f"{ramUsage:.2f} MB")

        await ctx.send(content=f"ℹ About **{ctx.bot.user}** :henpog:", embed=embed)

    @commands.command(aliases=["streaming","stream"])
    async def is_streaming(self, ctx, user : discord.Member = None):
        """Will check if you or the user on argument streams Dead Cells and posts a message in #streams channel"""
        user = user or ctx.author

        streaming_role = discord.utils.get(ctx.guild.roles, id=945020788090765343)
        streams_channel = self.bot.get_channel(386680735374901249)

        user_activities = user.activities
        activity = 0


        if not len(user_activities) > 0:
            raise Exception("no activity")

        for activity in user_activities:
            if activity.type is discord.ActivityType.streaming:
                print(activity.type)
                activity = activity

        if activity.game == "Dead Cells":
            print(activity)

            await streams_channel.send(content="{} **is streaming Dead Cells !**\n".format(user.mention,activity.name))
            await streams_channel.send(content="**{}** - {}".format(activity.name,activity.url))
            await user.add_roles(streaming_role)

   
                


def setup(bot):
    bot.add_cog(Information(bot))
