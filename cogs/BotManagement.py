import discord
from discord.ext import commands, tasks


def admin_or_owner():
    def pred(ctx):
        if ctx.author.id == 151087006989025281:
            return True
        elif discord.utils.get(ctx.author.roles, name="Discord Admin"):
            return True
        else:
            return False
    return commands.check(pred)

class ManagementCommands(commands.Cog, name="Management Commands"):
    def __init__(self, bot):
        self.bot = bot
        self.greylist_collection = bot.server_info_database['greylist']
        self.whitelist_collection = bot.server_info_database['whitelist']
        self.get_all_whitelisted_greylisted_channels.start()


    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, bot_extension):
        self.bot.load_extension(f'cogs.{bot_extension}')
        await ctx.send(f"Loaded the {bot_extension} cog")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, bot_extension):
        self.bot.unload_extension(f'cogs.{bot_extension}')
        await ctx.send(f"Unloaded the {bot_extension} cog")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, bot_extension):
        self.bot.unload_extension(f'cogs.{bot_extension}')
        self.bot.load_extension(f'cogs.{bot_extension}')
        await ctx.send(f"Reloaded the {bot_extension} cog")

    @tasks.loop(count=1)
    async def get_all_whitelisted_greylisted_channels(self):
        collection = await self.greylist_collection.find({}).to_list(length=None)
        if len(collection) != 0:
            for channel_dict in collection:
                channel = await self.bot.fetch_channel(channel_dict["_id"])
                self.bot.greylisted_channels.append(channel.id)

        collection = await self.whitelist_collection.find({}).to_list(length=None)
        if len(collection) != 0:
            for channel_dict in collection:
                channel = await self.bot.fetch_channel(channel_dict["_id"])
                self.bot.whitelisted_channels.append(channel.id)

    @commands.group(brief="Greylist Group Commands")
    async def greylist(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send(
                "This is a group command, use `howler whitelist help` to get list of subcommands under this command.")
            return

    @admin_or_owner()
    @greylist.command(name="enable", brief="Enables 20 second cooldown on commands in this channel.")
    async def _enable(self, ctx, channel: discord.TextChannel):
        if await self.greylist_collection.count_documents({"_id": channel.id}, limit=1) != 0:
            return await ctx.send("This channel is already greylisted.")

        channel_dict = {"_id": channel.id}

        await self.greylist_collection.insert_one(channel_dict)

        await ctx.send(f"Added {channel.name} to the greylist!")
        self.bot.greylisted_channels.clear()
        self.get_all_whitelisted_greylisted_channels.start()

    @admin_or_owner()
    @greylist.command(name="disable", brief="Disables cooldowns for commands in specified channel", description="Disables cooldowns for commands in specified channel. Disables commands if channel is not in whitelist.")
    async def _disable(self, ctx, channel: discord.TextChannel):
        if await self.greylist_collection.count_documents({"_id": channel.id}, limit=1) != 0:
            await self.greylist_collection.delete_one({"_id": channel.id})

            await ctx.send(f"Removed {channel.name} from the greylist!")
        else:
            await ctx.send(f"{channel.name} is not on the greylist!")
        self.bot.greylisted_channels.clear()
        self.get_all_whitelisted_greylisted_channels.start()

    @greylist.command(name="list", brief="Lists all greylisted commands.")
    async def _list(self, ctx):
        list_string = "```\n"
        for channel_id in self.bot.greylisted_channels:
            channel = await self.bot.fetch_channel(channel_id)

            list_string += f"{channel.name}\n"

        list_string += "```"

        embed = discord.Embed(
            title="Greylisted Channels",
            description=list_string
        )

        await ctx.send(embed=embed)

    @commands.group(brief="Whitelist Group Commands")
    async def whitelist(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send(
                "This is a group command, use `howler whitelist help` to get list of subcommands under this command.")
            return

    @admin_or_owner()
    @whitelist.command(brief="Enables all commands in specified channels.")
    async def enable(self, ctx, channel: discord.TextChannel):
        if await self.whitelist_collection.count_documents({"_id": channel.id}, limit=1) != 0:
            return await ctx.send("This channel is already whitelisted.")

        channel_dict = {"_id": channel.id}

        await self.whitelist_collection.insert_one(channel_dict)

        await ctx.send(f"Added {channel.name} to the whitelist!")
        self.bot.whitelisted_channels.clear()
        self.get_all_whitelisted_greylisted_channels.start()

    @admin_or_owner()
    @whitelist.command(brief="Disables all commands in specified channel.", description="Disables all commands in specified channel. If channel is greylisted commands will continue to work.")
    async def disable(self, ctx, channel: discord.TextChannel):
        if await self.whitelist_collection.count_documents({"_id": channel.id}, limit=1) != 0:
            await self.whitelist_collection.delete_one({"_id": channel.id})

            await ctx.send(f"Removed {channel.name} from the whitelist!")
        else:
            await ctx.send(f"{channel.name} is not on the whitelist!")
        self.bot.whitelisted_channels.clear()
        self.get_all_whitelisted_greylisted_channels.start()

    @whitelist.command(brief="Lists all whitelisted channels.")
    async def list(self, ctx):
        list_string = "```\n"
        for channel_id in self.bot.whitelisted_channels:
            channel = await self.bot.fetch_channel(channel_id)

            list_string += f"{channel.name}\n"

        list_string += "```"

        embed = discord.Embed(
            title="Whitelisted Channels",
            description=list_string
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ManagementCommands(bot))
