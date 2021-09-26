import discord
from discord.ext import commands, tasks


def has_custom_commands_role(ctx):
    if discord.utils.get(ctx.author.roles, name="Commands"):
        return True
    elif discord.utils.get(ctx.author.roles, name="Discord Admin"):
        return True
    else:
        return False


class ImageCommand:
    def __init__(self, command, file):
        self.command = command
        self.file = file


class Images(commands.Cog, name="Images"):
    def __init__(self, bot):
        self.bot = bot
        self.image_collection = bot.image_database['images']
        self.get_all_images.start()

    @tasks.loop(seconds=1, count=1)
    async def get_all_images(self):
        self.bot.image_commands.clear()
        collection = await self.image_collection.find({}).to_list(length=None)
        for document in collection:
            x = ImageCommand(document["_id"], document['file'])
            self.bot.image_commands.append(x)

    @commands.group(brief="Image Group Commands.")
    async def image(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send("This is a group command, use `howler help image` to get list of subcommands under this command.")
            return

    @image.command(brief="Adds a custom image command.")
    @commands.check(has_custom_commands_role)
    async def add(self, ctx, command):
        if await self.image_collection.count_documents({"_id": f"howler {command}"}, limit=1) != 0:
            return await ctx.send("This command name is already registered.")

        if ctx.message.attachments[0].content_type == "image/gif":
            file_name = f"howler{command}.gif"
        else:
            file_name = f"howler{command}.png"

        command_name = f"howler {command}"
        image_dict = {"_id": command_name, "file": file_name}
        await self.image_collection.insert_one(image_dict)
        await ctx.message.attachments[0].save(f"images/{file_name}")
        x = ImageCommand(command_name, file_name)
        self.bot.image_commands.append(x)

    @image.command(brief="Removes a custom image command.")
    @commands.check(has_custom_commands_role)
    async def remove(self, ctx, command):
        await self.image_collection.delete_many({"_id": f"howler {command}"})
        self.get_all_images.start()

    @image.command(brief="Lists all custom image commands.")
    async def list(self, ctx):
        list_string = "```"
        for command in self.bot.image_commands:
            list_string += f"{command.command}\n"

        list_string += "```"

        embed = discord.Embed(
            title="Image Commands",
            description=list_string
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Images(bot))
