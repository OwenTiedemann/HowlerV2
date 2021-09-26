import discord
from discord.ext import commands, tasks


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

    @commands.group()
    async def image(self, ctx):
        pass

    @image.command()
    @commands.has_role('Discord Admin')
    async def add(self, ctx, command):
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

    @image.command()
    @commands.has_role('Discord Admin')
    async def remove(self, ctx, command):
        await self.image_collection.delete_many({"_id": f"howler {command}"})
        self.get_all_images.start()

    @image.command()
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
