import discord
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self , client):
        self.client = client

    @commands.command()
    async def pop(self , ctx , width = 3):
        if width > 6 : return await ctx.send("The size cannot exceed 6")
        elif width <= 1 : return await ctx.send('The size must be greater than 1')
        element = '||pop||'
        content = ''
        for i in range(width):
            for j in range(width):
                content += element
            content += '\n'

        await ctx.send(content)

def setup(client):
    client.add_cog(Fun(client))