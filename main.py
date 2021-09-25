import discord
from discord.ext import commands
import motor.motor_asyncio
import datetime
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
MONGO_TOKEN = config['MONGODB']['token']
DISCORD_TOKEN = config['DISCORD']['token']

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=['howlertest ', 'Howlertest '], intents=intents)
bot.max_messages = 1000
bot.image_commands = []
bot.reaction_events = []
bot.text_commands = []

database_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_TOKEN)
bot.database = database_client['ArizonaCoyotesDiscord']
bot.trivia_database = database_client['database']
bot.image_database = database_client['images']
bot.articles_database = database_client['articlefeeds']
bot.reaction_event_database = database_client['reactionevents']

initial_extensions = ['cogs.reactions']

whitelisted_channels = ["test-commands"]
whitelisted_categories = []

_cd = commands.CooldownMapping.from_cooldown(1.0, 20.0, commands.BucketType.channel)  # from ?tag cooldown mapping

@bot.check
async def restrict_commands(ctx):
    if ctx.channel.name in whitelisted_channels:
        return True
    elif ctx.channel.category.id in whitelisted_categories:
        return True
    else:
        return False


@bot.check
async def cool_down_check(ctx):
    if ctx.channel.category.id in whitelisted_categories:
        return True
    if ctx.channel.name == "game-thread":
        bucket = _cd.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)
        return True
    else:
        return True

@bot.event
async def on_message(message):
    # ON MESSAGE:
    #   CHECKS IF MESSAGE INCLUDES REACTION EVENT TEXT
    #       ADDS REACTION
    #   CHECKS IF MESSAGE IS AN IMAGE COMMAND
    #       SENDS IMAGE
    x = message.content.lower()
    for event in bot.reaction_events:
        if event.text in x:
            if event.type == "custom":
                emoji = bot.get_emoji(event.reaction)
                await message.add_reaction(emoji)
            else:
                await message.add_reaction(event.name)
    if message.content.startswith(("howler ", "Howler ")):
        res = message.content[0].lower() + message.content[1:]
        for command in bot.image_commands:
            if res == command.command:
                file = discord.File(f"images/{command.file}")
                await message.channel.send(file=file)
                return

    await bot.process_commands(message)

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

    bot.run(DISCORD_TOKEN)
