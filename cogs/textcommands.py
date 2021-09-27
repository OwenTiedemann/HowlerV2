import discord
from discord.ext import commands, tasks


def has_custom_commands_role():
    def pred(ctx):
        if discord.utils.get(ctx.author.roles, name="Highlighter + News"):
            return True
        elif discord.utils.get(ctx.author.roles, name="Discord Admin"):
            return True
        else:
            return False

    return commands.check(pred)


class TextCommand:
    def __init__(self, command, text):
        self.command = command
        self.text = text


class TextCommands(commands.Cog, name="Text"):
    def __init__(self, bot):
        self.bot = bot
        self.text_collection = bot.text_database['text']
        self.get_all_text.start()

    @tasks.loop(seconds=1, count=1)
    async def get_all_text(self):
        self.bot.text_commands.clear()
        collection = await self.text_collection.find({}).to_list(length=None)
        for document in collection:
            x = TextCommand(document["_id"], document['text'])
            self.bot.text_commands.append(x)

    @commands.group(brief="Text Group Commands")
    async def text(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send(
                "This is a group command, use `howler help text` to get list of subcommands under this command.")
            return

    @has_custom_commands_role()
    @text.command(brief="Adds a custom text command.")
    async def add(self, ctx, command, *, text):
        if await self.text_collection.count_documents({"_id": f"howler {command}"}, limit=1) != 0:
            return await ctx.send("This command name is already registered.")

        command_name = f"howler {command}"
        text_dict = {"_id": command_name, "text": text}
        await self.text_collection.insert_one(text_dict)
        x = TextCommand(command_name, text)
        self.bot.text_commands.append(x)

    @has_custom_commands_role()
    @text.command(brief="Removes a custom text command.")
    async def remove(self, ctx, command):
        await self.text_collection.delete_many({"_id": f"howler {command}"})
        self.get_all_text.start()

    @text.command(brief="Lists all custom text commands.")
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
