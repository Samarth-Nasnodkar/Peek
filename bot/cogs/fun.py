import discord
from discord.ext import commands


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def pop(self, ctx, width=3):
        if width > 10:
            return await ctx.send("The size cannot exceed 10")
        elif width <= 1:
            return await ctx.send('The size must be greater than 1')
        element = '||pop||'
        content = (element*width + '\n')*width
        await ctx.send(content)


def setup(client):
    client.add_cog(Fun(client))
