import discord
from discord.ext import commands


class ManagementCommands(commands.Cog, name="Management Commands"):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.group()
    async def greylist(self, ctx):
        pass

    @greylist.command()
    async def enable(self, ctx, channel: discord.ChannelType):
        pass

    @greylist.command()
    async def disable(self, ctx, channel: discord.ChannelType):
        pass

    @greylist.command()
    async def list(self, ctx):
        pass

    @commands.group()
    async def whitelist(self, ctx):
        pass

    @whitelist.command()
    async def enable(self, ctx, channel: discord.ChannelType):
        pass

    @whitelist.command()
    async def disable(self, ctx, channel: discord.ChannelType):
        pass

    @whitelist.command()
    async def list(self, ctx):
        pass


def setup(bot):
    bot.add_cog(ManagementCommands(bot))
