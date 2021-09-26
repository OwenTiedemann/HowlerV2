import discord
from discord.ext import commands, tasks


class TextCommand:
    def __init__(self, command, text):
        self.command = command
        self.text = text


class TextCommands(commands.Cog, name="Text"):
    def __init__(self, bot):
        self.bot = bot
        self.text_collection = bot.text_database['images']
        self.get_all_text.start()

    @tasks.loop(seconds=1, count=1)
    async def get_all_text(self):
        self.bot.text_commands.clear()
        collection = await self.text_collection.find({}).to_list(length=None)
        for document in collection:
            x = TextCommand(document["_id"], document['text'])
            self.bot.text_commands.append(x)

    @commands.group()
    async def text(self, ctx):
        pass

    @text.command()
    @commands.has_role('Discord Admin')
    async def add(self, ctx, command, *, text):
        if await self.text_collection.count_documents({"_id": f"howler {command}"}, limit=1) != 0:
            return await ctx.send("This command name is already registered.")

        command_name = f"howler {command}"
        text_dict = {"_id": command_name, "text": text}
        await self.text_collection.insert_one(text_dict)
        x = TextCommand(command_name, text)
        self.bot.text_commands.append(x)

    @text.command()
    @commands.has_role('Discord Admin')
    async def remove(self, ctx, command):
        await self.text_collection.delete_many({"_id": f"howler {command}"})
        self.get_all_text.start()

    @text.command()
    async def list(self, ctx):
        list_string = "```"
        for command in self.bot.text_commands:
            list_string += f"{command.command}\n"

        list_string += "```"

        embed = discord.Embed(
            title="Text Commands",
            description=list_string
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(TextCommands(bot))
