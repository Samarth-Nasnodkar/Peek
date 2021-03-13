import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient

class Levels(commands.Cog):
    def __init__(self , client):
        self.client = client
        self.cluster = MongoClient("mongodb+srv://dbBot:samarth1709@cluster0.moyjp.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")


    @comamnds.Cog.listener()
    async def on_message(self , message):
        if not message.author.bot: 
            db = self.cluster['main']
            collection = db['levels']
            levels = collection.find_one({'_id' : 3})
            if str(message.author.id) in levels.keys():
                collection.update_one({'_id' : 3} , {'$set' : {str(message.author.id) : levels[str(message.author.id)] + 0.05}})
            else:
                collection.update_one({'_id' : 3} , {'$set' : {str(message.author.id) : 0.05}})

        await self.client.process_commands(message)

def setup(client):
    client.add_cog(Levels(client))