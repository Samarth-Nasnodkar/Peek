import discord
from discord.ext import commands
from pymongo import MongoClient
from os import environ

cluster = MongoClient(environ.get('mongo_url'))


def get_prefix(client, message):
    db = cluster["main"]
    collection = db["entry"]
    prefixes = collection.find_one({"_id": 0})
    try:
        if prefixes is None:
            return "$"
        elif str(message.guild.id) in prefixes.keys():
            return prefixes[str(message.guild.id)]
        return "$"
    except:
        return "$"


def update_prefix(prefix, guild_id):
    db = cluster['main']
    collection = db['entry']
    prefixes = collection.find_one({'_id': 0})
    if prefixes is None:
        collection.insert_one({'_id': 0, str(guild_id): prefix})
        return True
    else:
        collection.update_one({'_id': 0}, {'$set': {str(guild_id): prefix}})
        return True


intents = discord.Intents.all()
client = commands.Bot(command_prefix=get_prefix, intents=intents, case_insensitive=True)
client.remove_command('help')


@client.event
async def on_ready():
    print("Bot online")

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! In {round(client.latency * 1000)}ms')

@client.event
async def on_message(message):
    if not message.author.bot:
        db = cluster['main']
        collection = db['levels']
        levels = collection.find_one({'_id': 3})
        if str(message.author.id) in levels.keys():
            collection.update_one({'_id': 3}, {'$set': {str(message.author.id): levels[str(message.author.id)] + 0.05}})
        else:
            collection.update_one({'_id': 3}, {'$set': {str(message.author.id): 0.05}})

    await client.process_commands(message)


TOKEN = environ.get('discord_bot_token')
client.load_extension("cogs.moderation")
client.load_extension("cogs.economy")
client.load_extension('cogs.memes')
client.load_extension('cogs.fun')
client.run(TOKEN)
