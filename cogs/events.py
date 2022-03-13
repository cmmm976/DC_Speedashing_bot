import discord
import psutil
import os
import asyncio

from datetime import datetime
from discord.ext import commands
from discord.ext.commands import errors
from utils import default


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.config()
        self.process = psutil.Process(os.getpid())

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            await ctx.send_help(helper)

        elif isinstance(err, errors.CommandInvokeError):
            error = default.traceback_maker(err.original)

            if "2000 or fewer" in str(err) and len(ctx.message.clean_content) > 1900:
                return await ctx.send(
                    "You attempted to make the command display more than 2,000 characters...\n"
                    "Both error and command will be ignored."
                )

            await ctx.send(f"There was an error processing the command ;-;\n{error}")

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.MaxConcurrencyReached):
            await ctx.send("You've reached max capacity of command usage at once, please finish the previous one...")

        elif isinstance(err, errors.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown... try again in {err.retry_after:.2f} seconds.")

        elif isinstance(err, errors.CommandNotFound):
            pass
        
        elif isinstance(err, errors.UserInputError):
            await ctx.send(err)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        to_send = next((
            chan for chan in sorted(guild.channels, key=lambda x: x.position)
            if chan.permissions_for(guild.me).send_messages and isinstance(chan, discord.TextChannel)
        ), None)

        if to_send:
            await to_send.send(self.config["join_message"])

    @commands.Cog.listener()
    async def on_command(self, ctx):
        try:
            print(f"{ctx.guild.name} > {ctx.author} > {ctx.message.clean_content}")
        except AttributeError:
            print(f"Private message > {ctx.author} > {ctx.message.clean_content}")

    @commands.Cog.listener()
    async def on_ready(self):
        """ The function that activates when boot was completed """
        if not hasattr(self.bot, "uptime"):
            self.bot.uptime = datetime.now()

        # Check if user desires to have something other than online
        status = self.config["status_type"].lower()
        status_type = {"idle": discord.Status.idle, "dnd": discord.Status.dnd}

        # Check if user desires to have a different type of activity
        activity = self.config["activity_type"].lower()
        activity_type = {"listening": 2, "watching": 3, "competing": 5}

        await self.bot.change_presence(
            activity=discord.Game(
                type=activity_type.get(activity, 0), name=self.config["activity"]
            ),
            status=status_type.get(status, discord.Status.online)
        )

        # Indicate that the bot has successfully booted up
        print(f"Ready: {self.bot.user} | Servers: {len(self.bot.guilds)}")

    
    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        global cooldown
        cooldown = []
        if before in cooldown:
            return
        cooldown.append(before)
        await asyncio.sleep(3600*2) # here you can change how long the cooldown should be
        cooldown.remove(before)

        streaming_role = after.guild.get_role(945020788090765343)
        streams_channel = self.bot.get_channel(386680735374901249)

        try:
            activities = [activity for activity in after.activities]
        except:
            pass
        for activity in activities:
            if not (activity.type is discord.ActivityType.streaming):
                print("{} activity_type (should be non streaming) ->".format(after.name), activity.type)
                # User is doing something other than streaming
                if streaming_role in after.roles:
                    print(f"{after.display_name} has stopped streaming")
                    await after.remove_roles(streaming_role)
            else:
                print("{} activity_type in else (should be streaming) -> ".format(after.name), activity.type)
                if streaming_role not in after.roles and activity.game == "Dead Cells":
                    # If they don't have the role, give it to them
                    # If they have it, we already know they're streaming so we don't need to do anything
                    print(f"{after.display_name} has started streaming")
                    await after.add_roles(streaming_role)
                    await streams_channel.send(content="{} **is streaming Dead Cells !**\n**{}** - {}".format(after.mention,activity.name, activity.url))
                    break

    @commands.Cog.listener()
    async def on_message(self, message):
        last_message = (await message.channel.history(limit=2).flatten())[1]
        if last_message.content == message.content:
            await message.delete()



def setup(bot):
    bot.add_cog(Events(bot))
