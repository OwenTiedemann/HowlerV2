import discord
import tweepy
from discord.ext import commands, tasks
import configparser
import json

config = configparser.ConfigParser()
config.read('config.ini')
CONSUMER_KEY = config['TWITTER']['consumer_key']
CONSUMER_SECRET_KEY = config['TWITTER']['consumer_secret_key']
ACCESS_TOKEN = config['TWITTER']['access_token']
ACCESS_TOKEN_SECRET = config['TWITTER']['access_token_secret']

channel_list = []
name_list = []
id_list = []
user_list = []
status_list = []

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)


class MyStreamListener(tweepy.Stream):

    # def on_status(self, status): #adds status to list
    # status_list.append(status)

    def on_data(self, status):
        status_list.append(status)

    def on_error(self, status_code):
        print('ERROR: ' + str(status_code))  # prints error code on error, mostly rate limited
        return True

    def on_exception(self, error):
        print('exception', error)  # restarts the stream after an exception
        run_stream()
        print('Restarting stream!')


def run_stream():  # runs twitter stream
    my_stream_listener = MyStreamListener(consumer_key=CONSUMER_KEY,
                                          consumer_secret=CONSUMER_SECRET_KEY,
                                          access_token=ACCESS_TOKEN,
                                          access_token_secret=ACCESS_TOKEN_SECRET)
    my_stream_listener.filter(follow=id_list, threaded=True)


def fill_list():
    for user_id, channel_id, name in zip(id_list, channel_list, name_list):
        x = TwitterUser(str(user_id), channel_id, name)
        user_list.append(x)

    run_stream()


class TwitterUser:  # class for Twitter feeds
    def __init__(self, user_id, channel, name):
        self.user_id = user_id
        self.channel = channel
        self.name = name
        self.status = 0
        self.old_status = 0


class TweetBot(commands.Cog, name="Twitter"):
    def __init__(self, bot):
        self.bot = bot
        self.get_twitter_users.start()  # on start up pulls twitter feed data from database
        self.check_status.start()  # checks status list for tweets from followed feeds
        self.post_tweet.start()  # posts tweets from followed feeds

    @tasks.loop(seconds=1, count=1)
    async def get_twitter_users(self):
        feeds_collection = self.bot.database['Twitter Feeds']
        feeds = await feeds_collection.find().to_list(length=None)
        for feed in feeds:
            id_list.append(str(feed['_id']))
            channel_list.append(feed['channel'])
            name_list.append(feed['name'])

    @get_twitter_users.after_loop
    async def call_fill_list(self):
        fill_list()

    @tasks.loop(seconds=1)
    async def check_status(self):
        if status_list:
            status = status_list[0]  # pulls first item from list
            status_list.pop(0)  # deletes it from list
            tweet = json.loads(status)
            if 'user' in tweet:
                if str(tweet['user']['id']) in id_list:  # checks if user is one of followed feeds
                    for user in user_list:  # finds the user object
                        if str(tweet['user']['id']) == user.user_id:
                            user.status = tweet  # sets the objects status
                            break  # ends loop

    @tasks.loop(seconds=5)
    async def post_tweet(self):
        for user in user_list:  # goes through all followed feeds
            if user.status != user.old_status:  # checks if there is a new tweet
                channel = self.bot.get_channel(int(user.channel))  # gets channel
                tweet_id = str(user.status['id'])
                tweet_name = str(user.status['user']['name'])
                if 'retweeted_status' in user.status:
                    await channel.send(f'{tweet_name} retweeted https://twitter.com/twitter/statuses/' + tweet_id)
                else:
                    await channel.send(f'{tweet_name} tweeted https://twitter.com/twitter/statuses/' + tweet_id)
                user.old_status = user.status  # updates old tweet

    @post_tweet.before_loop
    async def before_post_tweet(self):
        print('waiting...')
        await self.bot.wait_until_ready()

    @commands.group(brief="Twitter Group Commands")
    async def twitter(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send("Group of commands related to Twitter, for more info use howler help twitter")

    @twitter.command(name="add", brief="Add a twitter feed")
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.has_role('Discord Admin')
    async def _add(self, ctx, channel: discord.TextChannel, handle: str):
        feeds_collection = self.bot.database['Twitter Feeds']

        try:
            user = api.get_user(screen_name=handle)  # gets user id of inputted handle
            user_id = user.id
        except Exception as inst:
            print(inst)
            await ctx.send("Could not find that twitter user, please try again.")
            return

        feed_dict = {"_id": str(user_id), "channel": channel.id, "name": handle}

        try:
            await feeds_collection.insert_one(feed_dict)  # inserts the feed into the database
        except Exception as exception:
            print(exception)
            await ctx.send("Could not add, possibly already followed.")
            return

        channel_list.append(channel.id)  # adds feed to lists for stream
        id_list.append(str(user.id))
        name_list.append(handle)
        fill_list()

        await ctx.send(f"Now following {handle}")

    @twitter.command(name="remove", brief="Remove a Twitter feed")
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.has_role('Discord Admin')
    async def _remove(self, ctx, handle: str):
        feeds_collection = self.bot.database['Twitter Feeds']
        feeds = await feeds_collection.find().to_list(length=None)  # converts collection cursor to list
        for feed in feeds:
            if feed['name'] == handle:
                await feeds_collection.delete_many(feed)  # deletes the database section for that feed
                await ctx.send('Unfollowed that feed!')
                user_list.clear()  # resets the lists in prep for stream restart
                id_list.clear()
                name_list.clear()
                self.get_twitter_users.start()  # restarts stream
                return

    @twitter.command(name="list", brief="Show list of all Twitter feeds")
    async def _list(self, ctx):
        s = "\n"
        name_list_string = s.join(name_list)

        embed = discord.Embed(
            title="Twitter Feeds",
            description=name_list_string,
        )

        await ctx.send(embed=embed)  # shows list of all current twitter feeds


def setup(bot):
    bot.add_cog(TweetBot(bot))
